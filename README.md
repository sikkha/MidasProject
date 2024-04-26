# MidasProject

## Overview
MidasProject integrates cutting-edge AI with geopolitical analysis to redefine Global Macro Investment Strategies. Amidst escalating global tensions, such as the Ukraine-Russia conflict, our Meta-Geopolitical Framework employs advanced analytics to evaluate geopolitical dynamics and their implications on investments. This innovative approach is designed to optimize portfolio management for high-caliber entities like sovereign wealth funds, emphasizing long-term societal benefits and advancing global financial stability.

## Key Features

- **Advanced AI Integration**: Leverage sophisticated AI to analyze and predict geopolitical impacts on investments.
- **Socially Responsible Investing**: Focus on long-term societal benefits, moving beyond traditional profit-driven motives.
- **Risk Mitigation**: Enhance financial stability with proactive risk management, improved governance standards, and increased transparency.

## Getting Started

### Prerequisites

Ensure you have Python installed on your system (Python 3.6+ recommended). You will also need to install dependencies from the `requirements.txt` file:

```
bash
pip install -r requirements.txt
```

## Running the Trend Radar Scripts

MidasProject includes a series of scripts (`neopulsarwave_stage1.py` to `neopulsarwave_stage6.py`) that execute various stages of our analysis, from reading tweets to advanced data processing. To automate these scripts on a daily or weekly basis, use the provided shell script `run_neopulsarwave.sh`.

To schedule this script to run automatically:

1. Open your terminal.
2. Use `crontab` to edit your cron jobs:

```
bash
crontab -e
```

3. Add a line to schedule the script daily or weekly. For daily execution at 1 AM:

```
0 1 * * * /path/to/run_neopulsarwave.sh
```

Replace /path/to/run_neopulsarwave.sh with the actual path to the script.

## Starting the Frontend

To run the frontend of the MidasProject, you can use the following command:

```
python app.py &
```

Alternatively, to keep the server running in the background persistently, especially after closing the terminal, you can use screen or a similar tool:

```
screen 
python app.py
```
and use ctrl-a, d to exit from the current screen. This command starts app.py in a detached screen session named midas_frontend.


## Contributing

Contributions to MidasProject are welcome! Please read CONTRIBUTING.md for details on our code of conduct, and the process for submitting pull requests to us.
License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## Acknowledgments

 * Thanks to all contributors who have invested their time in improving this project.
 * Special thanks to entities and individuals committed to advancing socially responsible investing.

