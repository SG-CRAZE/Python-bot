import traceback

try:
    import discord
    from discord.ext import commands
    import subprocess
    import tempfile
    import os

    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix='/', intents=intents)

    @bot.command(name="run")
    async def run(ctx):
        if not ctx.message.attachments:
            await ctx.send("Pythonコードファイルを添付してください。")
            return

        attachment = ctx.message.attachments[0]

        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, attachment.filename)
            await attachment.save(file_path)

            if not file_path.endswith(".py"):
                await ctx.send("Python (.py) ファイルのみ受け付けます。")
                return

            docker_command = [
                "docker", "run", "--rm",
                "-v", f"{tmpdir}:/app",
                "--network", "ネットワーク使用許可",
                "--memory", "RAM容量",
                "python:Pythonバージョン",
                "python", f"/app/{attachment.filename}"
            ]

            try:
                result = subprocess.run(
                    docker_command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=タイムアウト時間,
                    text=True
                )

                output = result.stdout + result.stderr

                if len(output) > 1900:
                    output = output[:1900] + "\n...(省略)..."

                await ctx.send(f"```py\n{output}\n```")

            except subprocess.TimeoutExpired:
                await ctx.send("実行がタイムアウトしました。")

    bot.run("ボットToken")

except Exception as e:
    with open("error.log", "w") as f:
        f.write(traceback.format_exc())
    input("エラーが発生しました。Enterを押すと終了します。")
