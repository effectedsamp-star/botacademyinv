import os

import discord
from discord import ui
from discord.ext import commands


BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

CHANNEL_ID = 1562833325742104652
ADMIN_USER_ID = 1416863224430596107
GLOBAL_CHAT_ID = 1562833325742104648


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


class ApplicationModal(ui.Modal):
    def __init__(self):
        super().__init__(title="Заявка в Academy Dislocation Mafia")

        self.name = ui.TextInput(
            label="1. Имя",
            style=discord.TextStyle.short,
            placeholder="Твоё игровое и реальное имя",
            max_length=100,
            required=True
        )

        self.reason = ui.TextInput(
            label="2. Почему именно Dislocation Mafia",
            style=discord.TextStyle.paragraph,
            placeholder="Объясни, почему ты достоин попасть в Dislocation Mafia",
            max_length=1000,
            required=True
        )

        self.famhistory = ui.TextInput(
            label="3. Фамхистори",
            style=discord.TextStyle.paragraph,
            placeholder="Перечисли семьи, фракции и свой опыт",
            max_length=1000,
            required=True
        )

        self.aim_history = ui.TextInput(
            label="4. Опыт стрельбы и откатов",
            style=discord.TextStyle.paragraph,
            placeholder="Опиши свой опыт в стрельбе и откатам",
            max_length=1000,
            required=True
        )

        self.goals = ui.TextInput(
            label="5. Чему хочешь научиться",
            style=discord.TextStyle.paragraph,
            placeholder="Что хочешь получить от Academy Dislocation Mafia",
            max_length=1000,
            required=True
        )

        self.add_item(self.name)
        self.add_item(self.reason)
        self.add_item(self.famhistory)
        self.add_item(self.aim_history)
        self.add_item(self.goals)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        applicant = interaction.user

        embed = discord.Embed(
            title="Новая заявка в Academy Dislocation Mafia",
            color=discord.Color.dark_red(),
            timestamp=discord.utils.utcnow()
        )

        embed.add_field(
            name="Заявитель",
            value=f"{applicant.mention}\nID: `{applicant.id}`",
            inline=False
        )

        embed.add_field(
            name="1. Имя",
            value=self.name.value,
            inline=False
        )

        embed.add_field(
            name="2. Почему именно Dislocation Mafia",
            value=self.reason.value,
            inline=False
        )

        embed.add_field(
            name="3. Фамхистори",
            value=self.famhistory.value,
            inline=False
        )

        embed.add_field(
            name="4. Опыт стрельбы и откатов",
            value=self.aim_history.value,
            inline=False
        )

        embed.add_field(
            name="5. Чему хочешь научиться",
            value=self.goals.value,
            inline=False
        )

        view = ApplicationDecisionView(applicant_id=applicant.id)

        try:
            admin = await bot.fetch_user(ADMIN_USER_ID)
            await admin.send(embed=embed, view=view)
        except discord.Forbidden:
            await interaction.followup.send(
                "Не удалось отправить заявку администратору. Возможно, у него закрыты ЛС.",
                ephemeral=True
            )
            return
        except discord.HTTPException:
            await interaction.followup.send(
                "Произошла ошибка при отправке заявки. Попробуй позже.",
                ephemeral=True
            )
            return

        await interaction.followup.send(
            "Заявка отправлена. Её рассмотрит руководство Dislocation Mafia.",
            ephemeral=True
        )

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        print(f"Ошибка в заявке: {error}")

        if interaction.response.is_done():
            await interaction.followup.send(
                "Произошла ошибка при обработке заявки.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "Произошла ошибка при обработке заявки.",
                ephemeral=True
            )


class ApplicationDecisionView(ui.View):
    def __init__(self, applicant_id):
        super().__init__(timeout=None)
        self.applicant_id = applicant_id
        self.decided = False

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != ADMIN_USER_ID:
            await interaction.response.send_message(
                "Рассматривать заявки может только руководство Dislocation Mafia.",
                ephemeral=True
            )
            return False

        return True

    @ui.button(label="Принять", style=discord.ButtonStyle.green)
    async def accept_button(self, interaction: discord.Interaction, button: ui.Button):
        await self.handle_decision(interaction, True)

    @ui.button(label="Отказать", style=discord.ButtonStyle.red)
    async def reject_button(self, interaction: discord.Interaction, button: ui.Button):
        await self.handle_decision(interaction, False)

    async def handle_decision(self, interaction: discord.Interaction, accepted):
        if self.decided:
            await interaction.response.send_message(
                "По этой заявке уже принято решение.",
                ephemeral=True
            )
            return

        await interaction.response.defer()
        self.decided = True

        try:
            applicant = await bot.fetch_user(self.applicant_id)
        except discord.HTTPException:
            await interaction.followup.send(
                "Не удалось найти заявителя.",
                ephemeral=True
            )
            return

        if accepted:
            status_text = "ПРИНЯТ"
            color = discord.Color.green()

            private_message = (
                "DISLOCATION MAFIA\n\n"
                "Твоя заявка в Academy Dislocation Mafia принята.\n\n"
                "Ты прошёл первый отбор. Скоро с тобой свяжется руководство."
            )
        else:
            status_text = "ОТКАЗАНО"
            color = discord.Color.red()

            private_message = (
                "DISLOCATION MAFIA\n\n"
                "Твоя заявка в Academy Dislocation Mafia отклонена.\n\n"
                "На данный момент ты не подошёл. Ты можешь подать новую заявку позже."
            )

        dm_status = "Результат отправлен заявителю в ЛС."

        try:
            await applicant.send(private_message)
        except discord.Forbidden:
            dm_status = "Не удалось написать заявителю: у него закрыты ЛС."
        except discord.HTTPException:
            dm_status = "Не удалось отправить результат заявителю в ЛС."

        global_chat = bot.get_channel(GLOBAL_CHAT_ID)

        if global_chat is None:
            try:
                global_chat = await bot.fetch_channel(GLOBAL_CHAT_ID)
            except discord.HTTPException:
                global_chat = None

        if global_chat is not None:
            result_embed = discord.Embed(
                title="Результат заявки в Academy Dislocation Mafia",
                description=(
                    f"{applicant.mention} — **{status_text}**\n\n"
                    f"Решение вынес: {interaction.user.mention}."
                ),
                color=color,
                timestamp=discord.utils.utcnow()
            )

            try:
                await global_chat.send(
                    content=applicant.mention,
                    embed=result_embed,
                    allowed_mentions=discord.AllowedMentions(
                        users=True,
                        roles=False,
                        everyone=False
                    )
                )
            except discord.HTTPException:
                dm_status += "\nНе удалось опубликовать результат в общем канале."

        for child in self.children:
            child.disabled = True

        if interaction.message is not None:
            try:
                await interaction.message.edit(view=self)
            except discord.HTTPException:
                pass

        await interaction.followup.send(dm_status, ephemeral=True)


class ApplicationView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Подать заявку в Academy", style=discord.ButtonStyle.danger, custom_id="dislocation_mafia_academy_apply")
    async def apply_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(ApplicationModal())


async def send_application_message():
    channel = bot.get_channel(CHANNEL_ID)

    if channel is None:
        try:
            channel = await bot.fetch_channel(CHANNEL_ID)
        except discord.HTTPException:
            print(f"Канал с ID {CHANNEL_ID} не найден.")
            return

    async for message in channel.history(limit=100):
        if message.author == bot.user and message.embeds:
            if message.embeds[0].title == "ACADEMY DISLOCATION MAFIA":
                print("Панель заявок уже существует.")
                return

    embed = discord.Embed(
        title="ACADEMY DISLOCATION MAFIA",
        description=(
            "Хочешь войти в состав?\n\n"
            "Dislocation Mafia не набирает случайных людей.\n\n"
            "Если ты готов работать, учиться, держать уровень и не сливаться "
            "после первой сложности — жми кнопку ниже.\n\n"
            "Слабым, ленивым и тем, кто ищет лёгкий вход, здесь не место."
        ),
        color=discord.Color.dark_red()
    )

    embed.add_field(
        name="Требования",
        value=(
            "1. Опры, мувики или нарезки должны быть загружены на YouTube либо RuTube.\n"
            "2. Ты обязан пройти проверку на мультифам.\n"
            "3. Играешь активно.\n"
            "4. Уважаешь состав, дисциплину и решения руководства."
        ),
        inline=False
    )

    embed.add_field(
        name="Как подать заявку",
        value=(
            "Нажми кнопку «Подать заявку в Academy» ниже.\n\n"
            "Заполни все 5 пунктов честно и по делу. "
            "Пустые отговорки и копипаст будут отклонены."
        ),
        inline=False
    )

    embed.set_footer(text="DISLOCATION MAFIA • ACADEMY")

    await channel.send(embed=embed, view=ApplicationView())
    print("Панель заявок Academy Dislocation Mafia отправлена.")


@bot.event
async def on_ready():
    print(f"Бот запущен как {bot.user}")

    bot.add_view(ApplicationView())

    await send_application_message()


if not BOT_TOKEN:
    raise RuntimeError(
        "Не найден DISCORD_BOT_TOKEN. Добавь токен в переменные окружения."
    )


bot.run(BOT_TOKEN)отправлена.")
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
