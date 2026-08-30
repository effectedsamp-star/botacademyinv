import os
import discord
from discord import ui
from discord.ext import commands


# ================= НАСТРОЙКИ =================

# Рекомендуется задать токен в переменной окружения DISCORD_BOT_TOKEN.
# Например в PowerShell:
# $env:DISCORD_BOT_TOKEN="ВАШ_НОВЫЙ_ТОКЕН"
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

CHANNEL_ID = 1543340680435204186
ADMIN_USER_ID = 1416863224430596107
GLOBAL_CHAT_ID = 1543348521393070200

# ==============================================


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


# ---------- Единственное модальное окно заявки ----------
class ApplicationModal(ui.Modal, title="Заявка в academy"):
    name = ui.TextInput(
        label="1. Имя",
        style=discord.TextStyle.short,
        placeholder="Ваше имя",
        max_length=100,
        required=True,
    )

    reason = ui.TextInput(
        label="2. Почему вы захотели к нам",
        style=discord.TextStyle.paragraph,
        placeholder="Расскажите, почему хотите именно в нашу академию",
        max_length=1000,
        required=True,
    )

    famhistory = ui.TextInput(
        label="3. Фамхистори",
        style=discord.TextStyle.paragraph,
        placeholder="Опишите вашу историю в семьях/фракциях",
        max_length=1000,
        required=True,
    )

    aim_history = ui.TextInput(
        label="4. Откаты стрельбы",
        style=discord.TextStyle.paragraph,
        placeholder="Расскажите про ваш опыт откатов/стрельбы",
        max_length=1000,
        required=True,
    )

    goals = ui.TextInput(
        label="5. Чему хотите научиться у нас",
        style=discord.TextStyle.paragraph,
        placeholder="Чему хотите научиться в academy",
        max_length=1000,
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Сразу отвечаем пользователю, чтобы Discord не показал ошибку Interaction Failed.
        await interaction.response.defer(ephemeral=True)

        applicant = interaction.user

        embed = discord.Embed(
            title="🎓 Новая заявка в academy Pivo Syndicate",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow(),
        )

        embed.add_field(
            name="👤 Пользователь",
            value=f"{applicant.mention}\n`{applicant.id}`",
            inline=False,
        )
        embed.add_field(
            name="1. Имя",
            value=self.name.value,
            inline=False,
        )
        embed.add_field(
            name="2. Почему хочет к нам",
            value=self.reason.value,
            inline=False,
        )
        embed.add_field(
            name="3. Фамхистори",
            value=self.famhistory.value,
            inline=False,
        )
        embed.add_field(
            name="4. Откаты стрельбы",
            value=self.aim_history.value,
            inline=False,
        )
        embed.add_field(
            name="5. Чему хочет научиться",
            value=self.goals.value,
            inline=False,
        )

        embed.set_footer(
            text=f"Заявитель: {applicant} | ID: {applicant.id}"
        )

        view = ApplicationDecisionView(applicant_id=applicant.id)

        try:
            admin = await bot.fetch_user(ADMIN_USER_ID)
            await admin.send(embed=embed, view=view)

        except discord.Forbidden:
            await interaction.followup.send(
                "Не удалось отправить заявку администратору. "
                "Возможно, у администратора закрыты личные сообщения.",
                ephemeral=True,
            )
            return

        except discord.HTTPException:
            await interaction.followup.send(
                "Произошла ошибка при отправке заявки. Попробуйте позже.",
                ephemeral=True,
            )
            return

        await interaction.followup.send(
            "✅ Ваша заявка отправлена и находится **на проверке**. "
            "Ожидайте решения в личных сообщениях.",
            ephemeral=True,
        )

    async def on_error(
        self,
        interaction: discord.Interaction,
        error: Exception,
    ):
        print(f"Ошибка в модальном окне заявки: {error}")

        if interaction.response.is_done():
            await interaction.followup.send(
                "Произошла ошибка при обработке заявки. Попробуйте позже.",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                "Произошла ошибка при обработке заявки. Попробуйте позже.",
                ephemeral=True,
            )


# ---------- Кнопки для администратора ----------
class ApplicationDecisionView(ui.View):
    def __init__(self, applicant_id: int):
        super().__init__(timeout=None)
        self.applicant_id = applicant_id
        self.decided = False

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Кнопки может использовать только указанный администратор.
        if interaction.user.id != ADMIN_USER_ID:
            await interaction.response.send_message(
                "❌ У вас нет доступа к рассмотрению этой заявки.",
                ephemeral=True,
            )
            return False

        return True

    @ui.button(
        label="Принять",
        style=discord.ButtonStyle.green,
    )
    async def accept_button(
        self,
        interaction: discord.Interaction,
        button: ui.Button,
    ):
        await self.handle_decision(interaction, accepted=True)

    @ui.button(
        label="Отказать",
        style=discord.ButtonStyle.red,
    )
    async def reject_button(
        self,
        interaction: discord.Interaction,
        button: ui.Button,
    ):
        await self.handle_decision(interaction, accepted=False)

    async def handle_decision(
        self,
        interaction: discord.Interaction,
        accepted: bool,
    ):
        if self.decided:
            await interaction.response.send_message(
                "По этой заявке уже принято решение.",
                ephemeral=True,
            )
            return

        # Сообщаем Discord, что обрабатываем нажатие.
        await interaction.response.defer()

        self.decided = True

        applicant = await bot.fetch_user(self.applicant_id)

        if accepted:
            status_text = "✅ **Принято**"
            color = discord.Color.green()

            private_message = (
                "🎓 Поздравляем! Ваша заявка в academy Pivo Syndicate "
                "**принята**.\n\n"
                "Скоро с вами свяжутся старшие академии."
            )
        else:
            status_text = "❌ **Отказано**"
            color = discord.Color.red()

            private_message = (
                "🎓 К сожалению, ваша заявка в academy Pivo Syndicate "
                "**отклонена**.\n\n"
                "Вы можете подать новую заявку позже, когда наберётесь опыта."
            )

        # Отправка результата пользователю в ЛС.
        try:
            await applicant.send(private_message)
            dm_status = "✅ Результат отправлен пользователю в ЛС."
        except discord.Forbidden:
            dm_status = "⚠️ Не удалось написать пользователю: у него закрыты ЛС."
        except discord.HTTPException:
            dm_status = "⚠️ Не удалось отправить результат пользователю в ЛС."

        # Публикация результата и упоминание пользователя в общем канале.
        global_chat = bot.get_channel(GLOBAL_CHAT_ID)

        if global_chat is None:
            try:
                global_chat = await bot.fetch_channel(GLOBAL_CHAT_ID)
            except discord.HTTPException:
                global_chat = None

        if global_chat is not None:
            result_embed = discord.Embed(
                title="🎓 Результат заявки в academy",
                description=(
                    f"{applicant.mention} — {status_text}\n"
                    f"Решение вынесено администратором {interaction.user.mention}."
                ),
                color=color,
                timestamp=discord.utils.utcnow(),
            )

            await global_chat.send(
                content=applicant.mention,
                embed=result_embed,
                allowed_mentions=discord.AllowedMentions(
                    users=True,
                    roles=False,
                    everyone=False,
                ),
            )

        # Отключаем кнопки в вашем ЛС.
        for child in self.children:
            child.disabled = True

        if interaction.message is not None:
            await interaction.message.edit(view=self)

        await interaction.followup.send(dm_status, ephemeral=True)


# ---------- Кнопка открытия заявки ----------
class ApplicationView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(
        label="Подать заявку в academy",
        style=discord.ButtonStyle.green,
        custom_id="apply_academy_button",
    )
    async def apply_button(
        self,
        interaction: discord.Interaction,
        button: ui.Button,
    ):
        await interaction.response.send_modal(ApplicationModal())


# ---------- Единоразовая отправка сообщения с кнопкой ----------
# ---------- Единоразовая отправка красивой панели с кнопкой ----------
async def send_application_message():
    channel = bot.get_channel(CHANNEL_ID)

    if channel is None:
        try:
            channel = await bot.fetch_channel(CHANNEL_ID)
        except discord.HTTPException:
            print(f"Канал с ID {CHANNEL_ID} не найден.")
            return

    # Проверяем, создавал ли бот эту панель ранее.
    # Проверяем именно заголовок Embed, потому что теперь текст находится не в msg.content.
    async for msg in channel.history(limit=100):
        if (
            msg.author == bot.user
            and msg.embeds
            and msg.embeds[0].title == "🎓 Academy Pivo Syndicate"
        ):
            print("Панель с кнопкой уже существует, отправка пропущена.")
            return

    embed = discord.Embed(
        title="🎓 Academy Pivo Syndicate",
        description=(
            "## Хочешь попасть в академию?\n\n"
            "Если ты хочешь **развиваться**, учиться и стать частью "
            "сильной команды — заполняй заявку в academy Pivo Syndicate.\n\n"
            "Нажми кнопку ниже, заполни анкету и дождись решения администрации."
        ),
        color=discord.Color.dark_gold(),
    )

    embed.add_field(
        name="📌 Требования для подачи",
        value=(
            "> **1.** Твои опры, мувики или нарезки должны быть "
            "загружены на YouTube либо RuTube.\n"
            "> **2.** Ты должен(на) быть готов(а) к проверке на мультифам.\n"
            "> **3.** Ты играешь исключительно легитно."
        ),
        inline=False,
    )

    embed.add_field(
        name="📝 Как подать заявку",
        value=(
            "Нажми зелёную кнопку **«Подать заявку в academy»** ниже. "
            "После этого откроется анкета из 5 вопросов."
        ),
        inline=False,
    )

    embed.set_footer(
        text="Pivo Syndicate • Academy"
    )

    await channel.send(
        embed=embed,
        view=ApplicationView(),
    )

    print("Красивая панель с кнопкой отправлена.")


# ---------- Запуск ----------
@bot.event
async def on_ready():
    print(f"Бот зашёл как {bot.user}")

    # Делает главную кнопку заявки рабочей после перезапуска.
    bot.add_view(ApplicationView())

    await send_application_message()


if not BOT_TOKEN:
    raise RuntimeError(
        "Токен не найден. Создайте переменную окружения DISCORD_BOT_TOKEN "
        "и поместите туда новый токен бота."
    )
if not BOT_TOKEN:
    raise RuntimeError(
        "Не найден DISCORD_BOT_TOKEN. "
        "Добавьте токен в переменные окружения Bothost."
    )

bot.run(BOT_TOKEN)
