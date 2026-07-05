### ROADMAP
- Enhance the system further by generating novel phenomena classes to test against.
- Potentially (!!!) force a greater degree of topology growth via targeting the champion/winner algorithm's specific topological weaknesses.

# Adaptive NEAT Engine (WIP)

An advanced, multi-task neuroevolution engine built on top of `neat-python`. This system demonstrates how a neural network can dynamically evolve its physical topology or structure, as to adapt to fundamentally different, sequential challenges without suffering from catastrophic forgetting.

## Core Concepts

In standard neural network training, adaptation is parametric (adjusting weights on a fixed network shape). In this system, adaptation is **topological** (structural). 

The engine exposes a population of networks to three categorically distinct "phenomena" in sequence. No single, static network shape can solve all three:
1. **XOR Boolean Logic:** Requires the evolution of hidden nodes (non-linear separability).
2. **Temporal Sequence Memory:** Requires the evolution of recurrent loopback connections to maintain state across timesteps.
3. **Gaussian Approximation:** Requires the evolution of activation function diversity (e.g., Gaussian, sine, absolute value) across hidden layers to fit a non-linear bell curve's rise and fall.

---

## Code Architecture

The project largely consists of the following modular components:

*   `adaptive_genome.py`: Subclasses `DefaultGenome` from `neat-python`. Implements a structural memory system (`adaptation_history`) that snapshots and registers exactly which new nodes or connections emerged during exposure to a specific phenomenon, ensuring they are preserved and merged during genetic crossover.
*   `phenomena.py`: Defines the abstract `Phenomenon` base class and houses the three concrete challenge environments. Also contains the `PhenomenonRegistry` (the Wheel State tracker) which manages sequential exposure and tracks adaptation progress.
*   `fitness.py`: Implements a multi-phenomena evaluator. Uses the **harmonic mean** of individual task scores to calculate composite fitness. Because the harmonic mean is heavily dominated by its lowest component, this forces massive evolutionary pressure to maintain performance on previous tasks (preventing catastrophic forgetting).
*   `wheel.py`: The central orchestrator (`AdaptationWheel`). Controls the exposure loop, runs the populations, stamps the winners, and runs the final **Immunity Verification** tests.
*   `visualize.py`: Generates two dynamic `matplotlib` plots: a dual-axis line chart tracking structural growth vs. generation, and an adaptation heatmap.
*   `main.py`: The execution entry point of the entire application.

---

## Installation & Environment Setup [WINDOWS]

Since this project runs in a local Windows virtual environment, follow these steps to ensure clean environment execution and avoid Windows App Execution Alias conflicts.

### 1. Clone The Repository (obviously) 
- Run the following in the CLI
```bash
git clone https://github.com/MHamzaS45/adaptive-neat-engine
```
OR Clone directly if using <b> Visual Studio Code-GitHub Tools Extension </b>

### 2. BEFORE YOU RUN!: Disable Windows App Store Execution Aliases
Windows has a built-in shortcut that redirects default `python` commands to the Microsoft Store. Disable this:
1. Open **Settings > Apps > Advanced app settings > App execution aliases**.
2. Find `python.exe` and `python3.exe` in the list and toggle them both to **OFF**.

### 3. Set Up Virtual Environment & Dependencies
Open PowerShell or Command Prompt inside your project root folder and execute:

```bash
# setup + activate virtual environment
python -m venv .venv

.\.venv\Scripts\activate

# install  required libraries mentioned in file
pip install -r requirements.txt
```

*(Ensure your IDE, such as VS Code, is configured to use the interpreter located at `.\.venv\Scripts\python.exe` by opening the Command Palette `Ctrl+Shift+P` -> `Python: Select Interpreter`)*

---

## Configuration (`neat_config.ini`)

The network's evolution parameters are defined inside `neat_config.ini`. Note that because we are utilizing our custom genome subclass, the main genome configuration header **must match the class name exactly**:

```ini
[NEAT]
fitness_criterion     = max
fitness_threshold     = 0.85
pop_size              = 150
reset_on_extinction   = True

[AdaptiveGenome]
# Must be named [AdaptiveGenome] to map to our custom class!
feed_forward            = False
initial_connection      = unconnected
activation_options      = sigmoid tanh relu gauss sin abs
# ... other standard NEAT configurations
```

---

## Running the Tests

To launch the full evolutionary process, run:

```bash
python main.py
```

### Measuring Efficiency and Verification

Once the engine finishes evolving, it automatically performs an **Immunity Verification** check, logging results to your terminal and saving two output charts:

1.  **`topology_growth.png` (Structural Parsimony):** 
    Look at the dual-axis chart showing Node and Connection counts. A highly efficient adaptive run will show step-like jumps directly at each dashed vertical line (when a new phenomenon is introduced) followed by flat lines. This proves the network only adds structural complexity in response to raw environmental demands, rather than growing randomly.
2.  **`immunity_heatmap.png` (Task Retention):**
    Each row is a task mapped from red (vulnerable/unadapted) to green (fully adapted/immune). An efficient run shows that once a row turns green, it remains solid green throughout all subsequent generations—demonstrating complete immunity to catastrophic forgetting.



