# RI wastewater → Slack

Every Tuesday, Thursday and Saturday morning, posts CDC's official COVID-19 wastewater activity level for the Field's Point plant (Providence) to Slack, with whether masks are required (High and above).

## Setup

1. **Slack webhook.** https://api.slack.com/apps → Create New App → From scratch → pick your workspace. Under **Incoming Webhooks**, switch it on, click **Add New Webhook to Workspace**, choose the channel, and copy the URL. Treat it like a password.
2. **GitHub repo.** Upload `wastewater_bot.py` and `.github/workflows/wastewater.yml`, keeping that folder path.
3. **Secret.** Settings → Secrets and variables → Actions → New repository secret: name `SLACK_WEBHOOK_URL`, value = the webhook URL.
4. **Test.** Actions tab → "RI wastewater to Slack" → Run workflow.

## Changing things

- Days or time: the `cron` line in the workflow (times are UTC; `2,4,6` = Tue, Thu, Sat).
- Circle colors, or which levels require masks: the `LEVELS` table near the top of `wastewater_bot.py`.
