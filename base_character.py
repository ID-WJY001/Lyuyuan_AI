# base_character.py

from __future__ import annotations

import copy
import json
import logging
import os
import random
import re
import traceback
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import requests

from Game_Storage import GameStorage

logger = logging.getLogger(__name__)

# 这里声明一个类型别名，表示“接受字符串和整数参数、返回字符串列表”的关键词提取函数
KeywordExtractor = Callable[[str, int], List[str]]


class BaseCharacter:
	"""可复用的 LLM 角色代理基类。

	Parameters
	----------
	config:
		包含配置选项的字典，例如 prompt 模板、系统消息、初始状态等。
	storage:
		可选的 `GameStorage` 实例，默认会在构造函数里创建一个指向 ``saves/`` 的实例。
	keyword_extractor:
		可选的关键词提取函数，若不提供则内部尝试使用 `jieba`，失败时回退到简单分词。
	"""

	# 默认的游戏状态模板，可被具体角色配置覆盖
	DEFAULT_STATE = {
		"closeness": 30,
		"discovered": [],
		"chapter": 1,
		"last_topics": [],
		"dialogue_quality": 0,
		"relationship_state": "初始阶段",
		"mood_today": "normal",
		"boredom_level": 0,
		"respect_level": 0,
	}

	# 默认的 LLM API 请求配置，可通过 config['api'] 覆盖
	DEFAULT_API = {
		"endpoint": "https://api.deepseek.com/v1/chat/completions",
		"model": "deepseek-chat",
		"temperature": 0.8,
		"max_tokens": 1500,
		"api_key_env": "DEEPSEEK_API_KEY",
		"timeout": 45,
	}

	def __init__(
		self,
		config: Dict,
		storage: Optional[GameStorage] = None,
		keyword_extractor: Optional[KeywordExtractor] = None,
	) -> None:
		# 读取基础配置：角色名称、prompt 模板路径、系统消息等
		self.config = config
		self.name = config.get("name", "Character")
		prompt_path = config.get("prompt_template_path")
		if not prompt_path:
			raise ValueError("config['prompt_template_path'] is required")
		self.prompt_template_path = Path(prompt_path).resolve()

		self.player_name: str = config.get("player_name", "陈辰")
		self.system_prompts: List[str] = list(config.get("system_prompts", []))
		self.welcome_message: Optional[str] = config.get("welcome_message")
		self.history_size: int = int(config.get("history_size", 100))
		self.api_settings: Dict = {**self.DEFAULT_API, **config.get("api", {})}
		self.scene_description: str = config.get("current_scene_description", "")

		# 拷贝初始状态模板，避免被意外修改
		initial_state_template = copy.deepcopy(self.DEFAULT_STATE)
		initial_state_template.update(copy.deepcopy(config.get("initial_state", {})))
		self._initial_state_template = initial_state_template

		self.storage = storage or GameStorage()
		self.keyword_extractor = keyword_extractor or self._build_keyword_extractor()

		self.dialogue_history: List[Dict[str, str]] = []
		self.game_state: Dict = copy.deepcopy(self._initial_state_template)

		self._prompt_template_cache: Optional[str] = None

	# ------------------------------------------------------------------
	# Lifecycle helpers

	def start_new_game(self, is_new_game: bool = False) -> Dict[str, object]:
		"""Reset runtime state and return payload for UI consumers."""

		self.game_state = copy.deepcopy(self._initial_state_template)
		self.dialogue_history = self._build_initial_messages(is_new_game=is_new_game)

		intro_text = ""
		for message in reversed(self.dialogue_history):
			if message.get("role") == "assistant":
				intro_text = message.get("content", "")
				break
		if not intro_text and self.welcome_message:
			intro_text = self.welcome_message

		return {
			"intro_text": intro_text,
			"game_state": self.get_state_snapshot(),
			"history": copy.deepcopy(self.dialogue_history),
		}

	def _build_initial_messages(self, is_new_game: bool = False) -> List[Dict[str, str]]:
		# 构建开局时的 system/assistant 消息，子类可覆写。
		messages = [{"role": "system", "content": prompt} for prompt in self.system_prompts]
		if not is_new_game and self.welcome_message:
			messages.append({"role": "assistant", "content": self.welcome_message})
		return messages

	def set_dialogue_history_size(self, size: int = 100) -> None:
		# 限制最小窗口到 10，避免被设置成过小值
		self.history_size = max(10, int(size))

	# ------------------------------------------------------------------
	# Core interaction methods

	def chat(self, user_input: str) -> str:
		"""Default chat flow with hooks for subclasses to customise."""

		print("\n" + "#" * 20 + f" NEW CHAT REQUEST ({self.name}) " + "#" * 20)
		print(f"User Input: {user_input}")

		# 1. 先处理调试命令或特殊输入
		special = self.handle_special_commands(user_input)
		if special is not None:
			return special

		# 2. 判断是否有剧情事件需要在 LLM 调用前拦截
		pre_response = self.handle_pre_chat_events(user_input)
		if pre_response is not None:
			return pre_response

		# 3. 调用 LLM 获取分析与回复
		print("\n[DEBUG] Step 1: Calling `think_and_chat`...")
		result = self.think_and_chat(user_input)
		print(f"[DEBUG] Step 2: `think_and_chat` returned -> {result}")
		if not isinstance(result, dict):
			logger.error("think_and_chat returned non-dict result: %s", type(result))
			result = {"analysis": None, "response": self.get_backup_reply(), "error": "invalid_return"}

		ai_response = result.get("response", self.get_backup_reply())
		analysis = result.get("analysis")

		print(f"[DEBUG] Step 3: Parsed AI Response -> '{ai_response}'")
		print(f"[DEBUG] Step 4: Parsed Analysis -> {analysis}")

		print("\n" + "=" * 20 + " LLM ANALYSIS RESULT " + "=" * 20)
		if isinstance(analysis, dict) and "error" not in analysis:
			print(f"Thought Process: {analysis.get('thought_process', 'N/A')}")
			print(
				f"Affection Delta: {analysis.get('affection_delta', 0)} "
				f"(Reason: {analysis.get('affection_delta_reason', 'N/A')})"
			)
		else:
			print("Analysis failed or not available.")
		print("=" * 53 + "\n")

		self.dialogue_history.append({"role": "user", "content": user_input})

		print("[DEBUG] Step 5: Updating game state...")

		# 4. 有结构化分析就更新状态，否则走失败回调
		if isinstance(analysis, dict) and "error" not in analysis:
			affection_delta, affection_raw = self._sanitize_delta(
				analysis.get("affection_delta", 0),
				field_name="affection_delta",
				min_value=-5,
				max_value=5,
			)
			boredom_delta, boredom_raw = self._sanitize_delta(
				analysis.get("boredom_delta", 0),
				field_name="boredom_delta",
				min_value=-3,
				max_value=3,
			)
			reason = analysis.get("affection_delta_reason", "N/A")
			print(
				f"--- [ACTION] APPLYING NEW DELTA: "
				f"Affection raw={affection_raw} -> applied={affection_delta}, "
				f"Boredom raw={boredom_raw} -> applied={boredom_delta} ---"
			)
			print(
				f"[NEW SYSTEM] Affection Delta (applied): {affection_delta} "
				f"(Reason: {reason})"
			)
			print(f"[NEW SYSTEM] Boredom Delta (applied): {boredom_delta}")
			self.apply_analysis_to_state(analysis, user_input, affection_delta, boredom_delta)
		else:
			print("[NEW SYSTEM] Analysis failed or not available.")
			self.handle_analysis_failure(result, user_input)

		self.dialogue_history.append({"role": "assistant", "content": ai_response})
		self._trim_history()

		print("[DEBUG] Step 6: Chat method finished. Returning response.")

		# 5. 最后执行后置事件，如剧情触发等
		post_response = self.handle_post_chat_events(user_input, analysis, ai_response)
		if post_response is not None:
			return post_response
		return ai_response

	def think_and_chat(self, user_input: str) -> Dict:
		"""Render prompt, call LLM API, and parse the structured response."""

		# 1. 从磁盘读取 prompt 模板（带缓存）
		try:
			prompt_template = self._load_prompt_template()
		except FileNotFoundError as exc:
			logger.exception("Prompt template file missing: %s", self.prompt_template_path)
			print(
				"错误: Prompt模板文件 '" + str(self.prompt_template_path) + "' 未找到！"
			)
			return {"analysis": None, "response": self.get_backup_reply(), "error": str(exc)}

		# 2. 根据当前状态与输入填充模板
		prompt_variables = self.build_prompt_variables(user_input)
		filled_prompt = prompt_template.format(**prompt_variables)

		# 3. 发起 LLM 请求并处理异常
		try:
			raw_output = self._call_llm(filled_prompt)
		except Exception as exc:  # noqa: BLE001 - we want to surface any failure
			logger.error("LLM call failed: %s", exc)
			logger.debug(traceback.format_exc())
			return {"analysis": None, "response": self.get_backup_reply(), "error": str(exc)}

		return self._parse_llm_output(raw_output)

	# ------------------------------------------------------------------
	# Hooks for subclasses

	def handle_special_commands(self, user_input: str) -> Optional[str]:
		"""Allow subclasses to intercept debug commands."""

		return None

	def handle_pre_chat_events(self, user_input: str) -> Optional[str]:
		"""Runs before the LLM call; return a string to short-circuit the flow."""

		return None

	def handle_post_chat_events(
		self,
		user_input: str,
		analysis: Optional[Dict],
		ai_response: str,
	) -> Optional[str]:
		"""Runs after state updates; return a string to override final reply."""

		return None

	def get_backup_reply(self) -> str:
		"""Fallback reply when LLM output is unavailable (must override)."""

		raise NotImplementedError("Subclasses must implement get_backup_reply().")

	# ------------------------------------------------------------------
	# Prompt & LLM helpers

	def build_prompt_variables(self, user_input: str) -> Dict[str, str]:
		"""Compose variables for the prompt template."""

		# 将对话历史和最近话题等信息整理成模板可用的数据结构
		history_str = self._format_history_for_prompt()
		topics = self.game_state.get("last_topics") or []
		topics_str = ", ".join(topics) if topics else "无"
		return {
			"relationship_state": self.game_state.get("relationship_state", "初始阶段"),
			"closeness": self.game_state.get("closeness", 30),
			"mood_today": self.game_state.get("mood_today", "normal"),
			"last_topics": topics_str,
			"current_scene_description": self.scene_description,
			"conversation_history": history_str,
			"user_input": user_input,
		}

	def _call_llm(self, filled_prompt: str) -> str:
		api_key_env = self.api_settings.get("api_key_env", "DEEPSEEK_API_KEY")
		api_key = os.environ.get(api_key_env)
		if not api_key:
			raise ValueError(f"API key not found in environment variable '{api_key_env}'")

		# 组装请求体，调用具体的聊天模型
		payload = {
			"model": self.api_settings.get("model", self.DEFAULT_API["model"]),
			"messages": [{"role": "user", "content": filled_prompt}],
			"temperature": self.api_settings.get("temperature", self.DEFAULT_API["temperature"]),
			"max_tokens": self.api_settings.get("max_tokens", self.DEFAULT_API["max_tokens"]),
		}

		headers = {
			"Content-Type": "application/json",
			"Authorization": f"Bearer {api_key}",
		}

		response = requests.post(
			self.api_settings.get("endpoint", self.DEFAULT_API["endpoint"]),
			headers=headers,
			json=payload,
			timeout=self.api_settings.get("timeout", self.DEFAULT_API["timeout"]),
		)
		if response.status_code != 200:
			print(f"API返回错误: {response.status_code} - {response.text}")
			raise RuntimeError(f"API Error {response.status_code}: {response.text}")

		data = response.json()
		print("----- RAW API RESPONSE JSON -----")
		print(data)
		print("-------------------------------")
		return data["choices"][0]["message"]["content"]

	def _load_prompt_template(self) -> str:
		if self._prompt_template_cache is None:
			with open(self.prompt_template_path, "r", encoding="utf-8") as fh:
				self._prompt_template_cache = fh.read()
		return self._prompt_template_cache

	def _parse_llm_output(self, llm_output: str) -> Dict:
		analysis_json, response_text = None, self.get_backup_reply()
		print("\n--- LLM Raw Output ---\n", llm_output, "\n----------------------\n")

		# 解析 <analysis> 标签以获取结构化 JSON
		analysis_match = re.search(r"<analysis>(.*?)</analysis>", llm_output, re.DOTALL)
		if analysis_match:
			json_str = analysis_match.group(1).strip()
			json_match = re.search(r"\{.*\}", json_str, re.DOTALL)
			if json_match:
				cleaned_json_str = json_match.group(0)
				try:
					analysis_json = json.loads(cleaned_json_str)
				except json.JSONDecodeError as exc:
					logger.error("Failed to decode analysis JSON: %s", exc)
					analysis_json = {"error": f"JSON解析失败: {exc}", "raw_json": cleaned_json_str}
			else:
				analysis_json = {"error": "在<analysis>标签内未找到有效的JSON结构。"}
		else:
			print("警告: 在LLM输出中未找到 <analysis> 标签。")

		# 解析 <response> 标签获取角色台词；若缺失则用剩余文本
		response_match = re.search(r"<response>(.*?)</response>", llm_output, re.DOTALL)
		if response_match:
			response_text = re.sub(r"</?response>", "", response_match.group(1)).strip()
		elif analysis_match:
			# If analysis exists but response tag missing, take remainder.
			response_text = llm_output.split("</analysis>")[-1].strip()
		else:
			print("警告: 在LLM输出中未找到 <response> 标签。")

		print(f"--- PRE-CLEAN RESPONSE_TEXT --- \nrepr(): {repr(response_text)}\n------------------------------")
		response_text = re.sub(r"</?response>", "", response_text).strip()
		print(f"--- POST-CLEAN RESPONSE_TEXT --- \nrepr(): {repr(response_text)}\n-----------------------------")

		return {"analysis": analysis_json, "response": response_text}

	def _format_history_for_prompt(self) -> str:
		dialogue_only = [msg for msg in self.dialogue_history if msg["role"] in {"user", "assistant"}]
		recent_dialogue = dialogue_only[-10:]
		if not recent_dialogue:
			return "（你们还没有开始对话）"
		lines = [
			f"{self.player_name}: {entry['content']}" if entry["role"] == "user" else f"{self.name}: {entry['content']}"
			for entry in recent_dialogue
		]
		return "\n".join(lines)

	def _coerce_int(self, value, *, default: int = 0, field_name: str = "value") -> int:
		"""Best-effort conversion of arbitrary JSON value to int."""

		if isinstance(value, bool):  # bool is subclass of int; treat as invalid here
			logger.warning("%s expected int but received bool; using default %s", field_name, default)
			return default
		if isinstance(value, (int, float)):
			return int(value)
		if isinstance(value, str):
			match = re.search(r"-?\d+", value)
			if match:
				return int(match.group(0))
		logger.warning("%s expected int-compatible value, got %r; using default %s", field_name, value, default)
		return default

	def _sanitize_delta(
		self,
		value,
		*,
		field_name: str,
		min_value: int,
		max_value: int,
	) -> Tuple[int, int]:
		"""Convert LLM-provided delta to int and clamp within safe bounds."""

		coerced = self._coerce_int(value, default=0, field_name=field_name)
		clamped = max(min(coerced, max_value), min_value)
		if coerced != clamped:
			logger.warning(
				"%s out of bounds (raw=%s, clamped=%s)", field_name, coerced, clamped
			)
			print(
				f"[WARN] {field_name} raw={coerced} 超出范围，已限制在 {min_value}~{max_value} 之间 (applied={clamped})"
			)
		return clamped, coerced

	# ------------------------------------------------------------------
	# State management

	def apply_analysis_to_state(
		self,
		analysis: Dict,
		user_input: str,
		affection_delta: Optional[int] = None,
		boredom_delta: Optional[int] = None,
	) -> None:
		if affection_delta is None or boredom_delta is None:
			affection_delta, _ = self._sanitize_delta(
				analysis.get("affection_delta", 0),
				field_name="affection_delta",
				min_value=-10,
				max_value=10,
			)
			boredom_delta, _ = self._sanitize_delta(
				analysis.get("boredom_delta", 0),
				field_name="boredom_delta",
				min_value=-5,
				max_value=5,
			)

		reason = analysis.get("affection_delta_reason", "N/A")
		print(f"[STATE] Applying affection delta {affection_delta} (Reason: {reason})")
		print(f"[STATE] Applying boredom delta {boredom_delta}")
		self._update_closeness(affection_delta)

		# 更新无聊度并合并话题标签
		current_boredom = self.game_state.get("boredom_level", 0)
		self.game_state["boredom_level"] = max(0, current_boredom + boredom_delta)

		if "triggered_topics" in analysis:
			topics = analysis.get("triggered_topics", [])
		else:
			topics = self._extract_topics(user_input)

		if topics:
			merged = list(dict.fromkeys(list(topics) + self.game_state.get("last_topics", [])))
			self.game_state["last_topics"] = merged[:5]
			print(f"[STATE] Updated last topics: {self.game_state['last_topics']}")

	def handle_analysis_failure(self, result: Dict, user_input: str) -> None:  # noqa: ARG002
		"""Hook for subclasses to react when analysis is unavailable."""

		# 默认只是打 warning，子类可覆写做额外处理
		logger.warning("Analysis missing or invalid; skipping state update.")

	def _update_closeness(self, delta: int) -> None:
		if not delta:
			return
		current = self.game_state.get("closeness", 30)
		new_value = max(0, min(100, current + delta))
		if new_value != current:
			print(f"好感度变化: {current} -> {new_value} (变化: {delta})")
			self.game_state["closeness"] = new_value
			self._update_relationship_state()
			if new_value >= 100 and "confession_triggered" not in self.game_state:
				print("亲密度达到100，下次对话将触发表白事件！")
				self.game_state["closeness"] = 100

	def _update_relationship_state(self) -> None:
		closeness = self.game_state.get("closeness", 30)
		if closeness >= 80:
			state = "亲密关系"
		elif closeness >= 60:
			state = "好朋友"
		elif closeness >= 40:
			state = "朋友"
		else:
			state = "初始阶段"
		self.game_state["relationship_state"] = state
		print(f"关系状态更新为: {self.game_state['relationship_state']}")

	# ------------------------------------------------------------------
	# Utility helpers

	def _trim_history(self) -> None:
		# 只保留最新的对话记录，并始终保留所有 system 消息
		if len(self.dialogue_history) <= self.history_size:
			return
		systems = [msg for msg in self.dialogue_history if msg["role"] == "system"]
		recent_size = self.history_size - len(systems)
		recent_dialogue = [msg for msg in self.dialogue_history if msg["role"] != "system"][-recent_size:]
		self.dialogue_history = systems + recent_dialogue

	def _extract_topics(self, text: str, top_k: int = 3) -> List[str]:
		if not text:
			return []
		try:
			return self.keyword_extractor(text, top_k) if self.keyword_extractor else []
		except Exception as exc:  # noqa: BLE001
			logger.debug("Keyword extraction failed: %s", exc)
			return []

	def _build_keyword_extractor(self) -> KeywordExtractor:
		try:
			from jieba import analyse as jieba_analyse  # type: ignore

			def extractor(text: str, top_k: int = 3) -> List[str]:
				return jieba_analyse.extract_tags(text, topK=top_k)

			return extractor
		except ModuleNotFoundError:
			logger.info("jieba not available; falling back to whitespace keyword extractor.")

			def fallback(text: str, top_k: int = 3) -> List[str]:
				tokens = [token.strip() for token in re.split(r"\s+", text) if token.strip()]
				return tokens[:top_k]

			return fallback

	# ------------------------------------------------------------------
	# Persistence helpers

	def save(self, slot) -> bool:
		if "closeness" in self.game_state:
			self.game_state["closeness"] = int(self.game_state["closeness"])
		data = {"history": self.dialogue_history, "state": self.game_state}
		return self.storage.save_game(data, slot)

	def load(self, slot) -> bool:
		data = self.storage.load_game(slot)
		if not data:
			return False

		self.dialogue_history = data.get("history", [])
		state = data.get("state", {})
		defaults = copy.deepcopy(self._initial_state_template)
		defaults.update(state)
		self.game_state = defaults
		self._update_relationship_state()
		return True

	def get_state_snapshot(self) -> Dict:
		"""Expose a shallow copy of the current state for external callers."""

		return copy.deepcopy(self.game_state)


__all__ = ["BaseCharacter"]