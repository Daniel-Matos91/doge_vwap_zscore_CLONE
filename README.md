# DOGEUSDT VWAP + ZScore Signals (30m)

Estratégia:
- VWAP intraday
- Z-Score de (close - VWAP) com lookback (padrão 80)
- Spike de volume (volume > vol_ma * VOL_SPIKE_MULT)
- Sinal confirmado no **fechamento** da barra (entrada sugerida no **open** da próxima)
- TP = TP_MULT × |entry − VWAP_entry|
- SL = VWAP_entry
- Janela horária opcional: `all` ou `lisbon_13_17`

## Como usar (GitHub Actions a cada 30min)
1. **Fork/clone** este repo.
2. Vá em **Settings → Secrets and variables → Actions → New repository secret** e crie:
   - `TELEGRAM_BOT_TOKEN` (token do seu bot)
   - `TELEGRAM_CHAT_ID` (chat id)
   - (opcional) `DISCORD_WEBHOOK`
3. Ajuste `config.py` se quiser mudar parâmetros/worker.
4. O workflow em `.github/workflows/alerts.yml` já agenda `*/30 * * * *`.

## Rodar local
```bash
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN="xxx"
export TELEGRAM_CHAT_ID="yyy"
python alert.py

