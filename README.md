
# Payments API Monitor

A Python-based monitoring and incident detection project designed to explore API reliability, HTTP availability, latency analysis, and incident lifecycle management in payment environments.

## Overview

Payments API Monitor is a technical portfolio project focused on observability and operational reliability.

It demonstrates fundamental concepts used in Production Support, Payment Operations, Site Reliability Engineering (SRE), and Incident Management.

The application monitors HTTP endpoints, collects response metrics, identifies consecutive failures, and reconstructs incident timelines from monitoring logs.

**Current version:** v0.7 (development)

## Features

- HTTP endpoint monitoring
- Configurable monitoring intervals
- HTTP response classification
- Request latency measurement
- Structured JSONL logging
- Success and failure rate calculations
- P50, P95, and P99 latency analysis
- Consecutive failure detection
- Incident state transitions
- Incident timeline reconstruction
- Deterministic incident identifiers
- JSONL incident history generation
- Automated unit tests

## Technologies

- Python 3
- Requests
- JSON / JSONL
- Git and GitHub
- Ubuntu / WSL2
- Visual Studio Code
- unittest

## Architecture

```text
payments-api-monitor/
├── monitor.py
├── metrics.py
├── incidents.py
├── incident_history.py
├── requirements.txt
├── README.md
├── .gitignore
└── tests/
    ├── __init__.py
    └── test_incidents.py
```

### Components

| Component | Responsibility |
|-----------|----------------|
| monitor.py | Performs HTTP checks and records monitoring data |
| metrics.py | Calculates availability samples, error rates, and latency percentiles |
| incidents.py | Detects incident state transitions |
| incident_history.py | Reconstructs incident records from monitoring history |
| tests/ | Automated incident detection tests |

## Installation

Clone the repository:

```bash
git clone https://github.com/ChinoRodrix/payments-api-monitor.git
cd payments-api-monitor
```

Create a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Usage

### Start API monitoring

```bash
python monitor.py
```

The monitor periodically requests the configured endpoint and records HTTP responses and latency.

Stop monitoring with `Ctrl+C`.

### Generate metrics

```bash
python metrics.py
```

Example output:

```text
Total checks: 10
Successful checks: 10
Failed checks: 0
Success rate: 100%

Average latency: 670.45 ms
P50: 661.45 ms
P95: 725.01 ms
P99: 728.77 ms
```

Values are illustrative and depend on the monitoring sample.

### Analyze incidents

```bash
python incidents.py
```

The detector evaluates monitoring records and identifies operational states.

### Generate incident history

```bash
python incident_history.py
```

Incident records are written to:

```text
data/incidents.jsonl
```

## Incident Lifecycle

The current implementation uses the following states:

| State | Description |
|-------|-------------|
| HEALTHY | No active failure condition |
| DEGRADED | Initial consecutive failures detected |
| CRITICAL | Three consecutive failures detected |
| RECOVERED | Three consecutive successful checks following a critical incident |

These are demonstration thresholds, not production incident severity classifications.

## Testing

Run the automated test suite:

```bash
python -m unittest discover -s tests -v
```

The initial test suite covers:

- Healthy operation
- Initial degradation
- Critical incident detection
- Successful recovery
- Incomplete recovery
- Recovery interrupted by another failure

## Current Limitations

This is a learning and portfolio project, not a production-ready monitoring platform.

Known limitations include:

- HTTP checks use a configured test endpoint.
- Incident history is reconstructed from existing logs.
- Incident history files are overwritten during reconstruction.
- Incident state is not persisted incrementally.
- Different HTTP endpoints are currently treated as separate monitoring identities.
- Latency thresholds are experimental.
- Availability estimates depend on the collected samples.
- No live dashboard or external alerting integration is implemented.

## Roadmap

- [x] HTTP monitoring
- [x] Structured logging
- [x] Latency percentiles
- [x] Incident detection
- [x] Incident lifecycle
- [x] Incident history reconstruction
- [x] Initial automated tests
- [ ] Stable service identity
- [ ] Incremental incident persistence
- [ ] Additional automated tests
- [ ] Incident analytics
- [ ] Alerting integration
- [ ] Observability dashboard

## Security

This project uses public testing endpoints and synthetic monitoring data.

No real payment card information, production credentials, or confidential transaction data is required.

## Author

Tiago Rodrigues

Payments Operations | Production Reliability | Incident Management

[LinkedIn](https://www.linkedin.com/in/tiago-rodrigues-ba027b111)
