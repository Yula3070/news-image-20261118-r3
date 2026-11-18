# The Day in World News — Wednesday 18 November 2026

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/yula3070/news-image-20261118-r3/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/yula3070/news-image-20261118-r3/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

Forty-five stories from six continents on a single front page: Bahrain
and Kuwait intercept Iran's drones, Xi welcomes Trump to Shenzhen, and
Voyager 1 passes one light-day from Earth.

## What is on the page

- **3 lead stories**, each with its own flat-vector illustration: the
  Gulf drone interceptions, the Shenzhen summit, and Voyager 1.
- **10 more illustrated stories** in two rows of five: the Kerch bridge
  span, Peltola's Alaska win, the EU's €45bn Ukraine loan, Cyclone
  Akvan, GTA VI on sale, the El Obeid drone strike, Gaza's floods,
  Nvidia's $115.8bn quarter, UK inflation at 3.6%, and gold's slide.
- **A flat world atlas** with numbered pins marking stories 1–13 and
  dots for briefs 14–45.
- **BY THE NUMBERS**: 141, 25.9bn km, 14.9m, 56–44.
- **ALSO**: 32 more stories from the day, numbered 14–45.

## How it was built

`draw_frontpage.py` draws the whole page with PIL — every picture is a
flat vector shape drawn in that file. No photos, no copied art.

```sh
python3 draw_frontpage.py   # writes entry.png (1024x1024, deterministic)
```

## Sources

Every story on the page happened, or was first reported, on Wednesday
18 November 2026. Reporting: Reuters, AP, AFP, BBC, Al Jazeera, ONS,
IMD, NASA, UN, Amnesty. Disputed claims are attributed to their source.

## License

MIT — see `LICENSE`.
