# Retico GRED 🤖✨

Retico modules for **GRED** (_Generative Robot Emotional Displays_) that generate robot behavior sequences given an emotion label, and can execute them on a Misty robot.

---

## 🔧 Installation

Clone the repo and install requirements:

```bash
git clone https://github.com/zihaurpang/retico-gred.git
cd retico-gred
````

---

## 📦 Model Download

The GRED model is hosted on Hugging Face. Download the latest from:

[bsu‑slim/gred‑misty](https://huggingface.co/bsu-slim/gred-misty)

Clone with:

```bash
git lfs install
git clone https://huggingface.co/bsu-slim/gred-misty
```

---

## 🎭 Supported Emotions

You can input one of these 6 emotion labels:

* `anger_frustration`
* `interest_desire`
* `confusion_sorrow_boredom`
* `joy_hope`
* `understanding_gratitude_relief`
* `disgust_surprise_alarm_fear`

---

## 🧠 Input Format

The module currently uses `GPTTextIU` from the [retico‑chatgpt](https://github.com/retico-team/retico-chatgpt) repo as its input interface. If `GPTTextIU` isn’t available, either:

1. Replace `GPTTextIU` with `retico_core.text.TextIU`, or
2. Define the following helper in `chatgpt.py`:

   ```python
   class GPTTextIU(retico_core.text.TextIU):
       @staticmethod
       def type():
           return retico_core.text.TextIU.type()
       def __repr__(self):
           return f"{self.type()} - ({self.creator.name()}): {self.get_text()}"
   ```

Then update `output_iu` by replacing `retico_core.text.TextIU` to `GPTTextIU`.

---

## 🎯 Output

A sequence of robot commands like:

```
drive_track_0_0_1 move_arm_both_51_80 display_face_resources_misty_faces_black_7_1
say_text_wow! drive_track_24_24_1 display_face_resources_misty_faces_black_8_1
move_head_0_-20_0_80 say_text_ah! display_face_resources_misty_faces_black_8_1
```

These are sent to Misty and executed in real time.

---

## 🔁 Execution on Misty

To actually execute generated behavior sequences on a Misty robot, subscribe your `GREDActionGenerator` to the `ActionExecutionModule` from [**retico-emro**](https://github.com/zihaurpang/retico-emro). Example:

```python
from retico_mistyrobot.mistyPy import Robot
from retico_emro.action_formatter import ActionExecutionModule
from retico_gred.gred_module import GREDActionGenerator, model, tokenizer, device
from retico_core.debug import DebugModule  # Optional, for debugging

ip = "YOUR_MISTY_IP"

# Initialize Misty connection and modules
robot    = Robot(ip)
executor = ActionExecutionModule(robot)
gred     = GREDActionGenerator(model, tokenizer, device, emotion="joy_hope")

# (Optional) Add debug logging
debug    = DebugModule()
gred.subscribe(debug)

# Subscribe the executor so GRED outputs go to Misty
gred.subscribe(executor)

```

---

## 🔗 Dependencies

* **Hugging Face 🤗 transformers** – to load `gred-misty`
* **retico-core** (for TextIU classes)
* **retico-chatgpt** (providing `GPTTextIU`)
* **retico-emro** – for `ActionExecutionModule`
* **retico-mistyrobot** – Misty robot interface
