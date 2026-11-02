import os

import discord
from discord import ui
from discord.ext import commands


# ================= НАСТРОЙКИ =================

BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

CHANNEL_ID = 1562833325742104652
ADMIN_USER_ID = 1416863224430596107
GLOBAL_CHAT_ID = 1562833325742104648

ORGANIZATION_NAME = "Dislocation Mafia"
ACADEMY_NAME = "Academy Dislocation Mafia"

# ==============================================


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


# ---------- Модальное окно заявки ----------
class ApplicationModal(ui.Modal, title="Заявка в Academy Dislocation Mafia"):
    name = ui.TextInput(
        label="1. Имя",
        style=discord.TextStyle.short,
        placeholder="Твоё реальное имя",
        max_length=100,
        required=True,
    )

    reason = ui.TextInput(
        label="2. Почему именно Dislocation Mafia",
        style=discord.TextStyle.paragraph,
        placeholder="Объясни, почему ты достоин попасть в Dislocation Mafia",
        max_length=1000,
        required=True,
    )

    famhistory = ui.TextInput(
        label="3. Фамхистори",
        style=discord.TextStyle.paragraph,
        placeholder="Перечисли семьи, фракции и свой опыт",
        max_length=1000,
        required=True,
    )

    aim_history = ui.TextInput(
        label="4. Опыт стрельбы / откатов",
        style=discord.TextStyle.paragraph,
        placeholder="Опиши свой опыт в стрельбе и откатам",
        max_length=1000,
        required=True,
    )

    goals = ui.TextInput(
        label="5. Чему хочешь научиться",
        style=discord.TextStyle.paragraph,
        placeholder="Что ты хочешь получить от Academy Dislocation Mafia",
        max_length=1000,
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        applicant = interaction.user

        embed = discord.Embed(
            title="🎓 Новая заявка в Academy Dislocation Mafia",
            color=discord.Color.dark_red(),
            timestamp=discord.utils.utcnow(),
        )

        embed.add_field(
            name="👤 Заявитель",
            value=f"{applicant.mention}\n`{applicant.id}`",
            inline=False,
        )
        embed.add_field(name="1. Имя", value=self.name.value, inline=False)
        embed.add_field(
            name="2. Почему именно Dislocation Mafia",
            value=self.reason.value,
            inline=False,
        )
        embed.add_field(name="3. Фамхистори", value=self.famhistory.value, inline=False)
        embed.add_field(
            name="4. Опыт стрельбы / откатов",
            value=self.aim_history.value,
            inline=False,
        )
        embed.add_field(
            name="5. Чему хочешь научиться",
            value=self.goals.value,
            inline=False,
        )

        embed.set_footer(text=f"Заявитель: {applicant} | ID: {applicant.id}")

        view = ApplicationDecisionView(applicant_id=applicant.id)

        try:
            admin = await bot.fetch_user(ADMIN_USER_ID)
            await admin.send(embed=embed, view=view)

        except discord.Forbidden:
            await interaction.followup.send(
                "❌ Не удалось отправить заявку администратору. "
                "Возможно, у него закрыты личные сообщения.",
                ephemeral=True,
            )
            return

        except discord.HTTPException:
            await interaction.followup.send(
                "❌ Произошла ошибка при отправке заявки. Попробуй позже.",
                ephemeral=True,
            )
            return

        await interaction.followup.send(
            "✅ Заявка отправлена.\n\n"
            "Теперь её рассмотрит руководство Dislocation Mafia. "
            "Не создавай новые заявки и жди решения.",
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
                "❌ Произошла ошибка при обработке заявки. Попробуй позже.",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                "❌ Произошла ошибка при обработке заявки. Попробуй позже.",
                ephemeral=True,
            )


# ---------- Кнопки решения по заявке ----------
class ApplicationDecisionView(ui.View):
    def __init__(self, applicant_id: int):
        super().__init__(timeout=None)
        self.applicant_id = applicant_id
        self.decided = False

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != ADMIN_USER_ID:
            await interaction.response.send_message(
                "❌ Рассматривать заявки может только руководство Dislocation Mafia.",
                ephemeral=True,
            )
            return False

        return True

    @ui.button(label="Принять", style=discord.ButtonStyle.green)
    async def accept_button(
        self,
        interaction: discord.Interaction,
        button: ui.Button,
    ):
        await self.handle_decision(interaction, accepted=True)

    @ui.button(label="Отказать", style=discord.ButtonStyle.red)
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

        await interaction.response.defer()

        self.decided = True

        try:
            applicant = await bot.fetch_user(self.applicant_id)
        except discord.HTTPException:
            await interaction.followup.send(
                "❌ Не удалось найти заявителя.",
                ephemeral=True,
            )
            return

        if accepted:
            status_text = "✅ **ПРИНЯТ**"
            color = discord.Color.green()

            private_message = (
                f"🎓 **Dislocation Mafia**\n\n"
                f"Твоя заявка в **Academy Dislocation Mafia** принята.\n\n"
                f"Ты прошёл первый отбор. Скоро с тобой свяжется руководство.\n"
                f"Не подведи."
            )
        else:
            status_text = "❌ **ОТКАЗАНО**"
            color = discord.Color.red()

            private_message = (
                f"🎓 **Dislocation Mafia**\n\n"
                f"Твоя заявка в **Academy Dislocation Mafia** отклонена.\n\n"
                f"На данный момент ты не подошёл. "
                f"Ты можешь подать новую заявку позже."
            )

        try:
            await applicant.send(private_message)
            dm_status = "✅ Результат отправлен заявителю в ЛС."
        except discord.Forbidden:
            dm_status = "⚠️ Не удалось написать заявителю: у него закрыты ЛС."
        except discord.HTTPException:
            dm_status = "⚠️ Не удалось отправить результат заявителю в ЛС."

        global_chat = bot.get_channel(GLOBAL_CHAT_ID)

        if global_chat is None:
            try:
                global_chat = await bot.fetch_channel(GLOBAL_CHAT_ID)
            except discord.HTTPException:
                global_chat = None

        if global_chat is not None:
            result_embed = discord.Embed(
                title="🎓 Результат заявки в Academy Dislocation Mafia",
                description=(
                    f"{applicant.mention} — {status_text}\n\n"
                    f"Решение вынес: {interaction.user.mention}."
                ),
                color=color,
                timestamp=discord.utils.utcnow(),
            )

            try:
                await global_chat.send(
                    content=applicant.mention,
                    embed=result_embed,
                    allowed_mentions=discord.AllowedMentions(
                        users=True,
                        roles=False,
                        everyone=False,
                    ),
                )
            except discord.HTTPException:
                dm_status += "\n⚠️ Не удалось опубликовать результат в общем канале."

        for child in self.children:
            child.disabled = True

        if interaction.message is not None:
            try:
                await interaction.message.edit(view=self)
            except discord.HTTPException:
                pass

        await interaction.followup.send(dm_status, ephemeral=True)


# ---------- Кнопка подачи заявки ----------
class ApplicationView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(
        label="Подать заявку в Academy",
        style=discord.ButtonStyle.danger,
        custom_id="dislocation_mafia_academy_apply",
    )
    async def apply_button(
        self,
        interaction: discord.Interaction,
        button: ui.Button,
    ):
        await interaction.response.send_modal(ApplicationModal())


# ---------- Панель заявки ----------
async def send_application_message():
    channel = bot.get_channel(CHANNEL_ID)

    if channel is None:
        try:
            channel = await bot.fetch_channel(CHANNEL_ID)
        except discord.HTTPException:
            print(f"Канал с ID {CHANNEL_ID} не найден.")
            return

    async for message in channel.history(limit=100):
        if (
            message.author == bot.user
            and message.embeds
            and message.embeds[0].title == "🎓 ACADEMY DISLOCATION MAFIA"
        ):
            print("Панель заявок уже существует. Новая панель не отправлена.")
            return

    embed = discord.Embed(
        title="🎓 ACADEMY DISLOCATIONAcademy Pivo Syndicate"
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
