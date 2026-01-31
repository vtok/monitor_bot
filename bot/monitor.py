import asyncio
import subprocess
import time
from datetime import timedelta

from bot.constants import CHAT_ID, TARGET_IP, PING_INTERVAL, STATE_CONFIRMATION

LIGHT_ON = True
LIGHT_OFF = False

def fmt_duration(seconds: float) -> str:
    return str(timedelta(seconds=int(seconds)))


class PingMonitor:
    def __init__(self):
        self.initialized = False
        # підтверджений стан
        self.current_state: bool = True
        self.state_start_ts: float | None = None

        # кандидат на підтвердження
        self.pending_state: bool | None = None
        self.pending_since: float | None = None

        # статистика
        self.total_up = 0.0
        self.total_down = 0.0

    def ping(self) -> bool:
        """
        True  -> ping OK
        False -> ping FAIL
        """
        try:
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "2", TARGET_IP],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return LIGHT_ON if not result.returncode else LIGHT_OFF
        except Exception:
            return False

    async def confirm_state(self, new_state: bool, now: float, app, initial: bool = False):
        msg = []

        # ================= INITIAL STATE =================
        if initial:
            self.current_state = new_state
            self.state_start_ts = now

            msg.append("ℹ️ Початковий стан після запуску бота")
            msg.append("")

            if new_state is LIGHT_ON:
                msg.append("🟢 Є світло")
            else:
                msg.append("🔴 Немає світла")

            await app.bot.send_message(
                chat_id=CHAT_ID,
                text="\n".join(msg)
            )
            return

        # ================= STATE CHANGE =================
        previous_state = self.current_state
        previous_duration = None

        # закриваємо попередній підтверджений стан
        if self.state_start_ts is not None:
            previous_duration = now - self.state_start_ts
            if previous_state is LIGHT_ON:
                self.total_up += previous_duration
            else:
                self.total_down += previous_duration

        # відкриваємо новий стан
        self.current_state = new_state
        self.state_start_ts = now

        # формуємо повідомлення
        if new_state is LIGHT_ON:
            msg.append("✅ Дали світло")
        else:
            msg.append("🚨 Зникло світло")

        if previous_state is not None and previous_duration is not None:
            msg.append("")
            state_text = "увімкнене" if previous_state is LIGHT_ON else "відсутнє"
            msg.append(
                f"⏱ Світло було {state_text}: "
                f"{fmt_duration(previous_duration)}"
            )

        msg.append("")
        msg.append("📊 Загальна статистика:")
        msg.append(f"🟢 Зі світлом:  {fmt_duration(self.total_up)}")
        msg.append(f"🔴 Без світла:  {fmt_duration(self.total_down)}")

        await app.bot.send_message(
            chat_id=CHAT_ID,
            text="\n".join(msg)
        )

    async def run(self, app):
        while True:
            now = time.time()
            detected_state: bool = self.ping()

            # перший запуск
            if self.pending_state is None:
                self.pending_state = detected_state
                self.pending_since = now
                await asyncio.sleep(PING_INTERVAL)
                continue

            # стан змінився → починаємо відлік стабільності
            if detected_state != self.pending_state:
                self.pending_state = detected_state
                self.pending_since = now
            else:
                # стан стабільний
                if now - self.pending_since >= STATE_CONFIRMATION:
                    # перше підтвердження після старту
                    if not self.initialized:
                        await self.confirm_state(self.pending_state, now, app, initial=True)
                        self.initialized = True

                    # звичайна зміна стану
                    elif self.pending_state != self.current_state:
                        await self.confirm_state(self.pending_state, now, app)

            await asyncio.sleep(PING_INTERVAL)

    def get_status(self) -> str:
        if self.current_state is None or self.state_start_ts is None:
            return "ℹ️ Стан ще не визначений, зачекай кілька секунд…"

        now = time.time()
        current_duration = now - self.state_start_ts

        # базові накопичені значення
        up = self.total_up
        down = self.total_down

        # додаємо активний стан
        if self.current_state is LIGHT_ON:
            up += current_duration
        else:
            down += current_duration

        state_text = "Є світло" if self.current_state is LIGHT_ON else "Немає світла"
        state_icon = "🟢" if self.current_state is LIGHT_ON else "🔴"

        return (
            "💡 Статус світла\n\n"
            f"{state_icon} ЗАРАЗ: {state_text}\n"
            f"⏱ Триває: {fmt_duration(current_duration)}\n\n"
            f"📊 Всього зі світлом:  {fmt_duration(up)}\n"
            f"📊 Всього без світла: {fmt_duration(down)}"
        )

monitor = PingMonitor()
