:::chapter 2 | Inside the Box: Neural Networks from C++ | Lectures 27–30 · first.cpp & trained.cpp · Good to know
- Why some problems need **learning** instead of `if/else`
- A **single neuron** = a linear equation
- **Training** = nudging weights with the error (**gradient descent**)
- The course's **C++ training program**, line by line, with its real output
- **Learning rate**, **epochs**, **training vs inference**
- Why stacking lines stays a line, and how **ReLU** fixes it
- How any curve can be built from ReLUs
- From one neuron to an **LLM**: embeddings, **attention**, transformers
- **Prompting vs RAG vs fine-tuning**
:::

In Lectures 27–30 Rohit steps back and asks: *what is actually inside the model?* He answers in **C++**, which is perfect for you. Interviewers for AI roles often ask "what is a neural network / gradient descent / activation function / attention?" — this chapter gives you short, correct answers.

## 2.1 Rules vs learning %%GOOD%%

Normal programming: **you** write the rules. Prime numbers, Fibonacci, sliding window, tree traversal — input goes in, your logic runs, the output is **deterministic**.

But some problems have no rules you can write down. *Is this photo a dog or a cat?* *Is this tweet supporting or opposing the claim?* You can't write `if (ears == pointy)`. What you **do** have is lots of **examples** (input → correct output).

> Machine learning = let the computer **find the function** from examples.

Rohit's whiteboard starts with an easy one. Hours studied → marks: 3 → 32, 4 → 42, 5 → 52, 6 → 62. You can guess the rule: `marks = 10 × study + 2`. A machine has to **find** that 10 and that 2 by itself.

## 2.2 One neuron = one linear equation %%GOOD%%

The course dataset has 1000 students with two inputs:

```text title="Lecture27and28/dataset.csv (first rows)"
study_hours,sleep_hours,marks
9,2,55
10,7,75
1,1,12
2,4,26
```

We guess the shape of the answer: `marks = w1 × study + w2 × sleep + b`. The numbers `w1`, `w2` are **weights** and `b` is the **bias**. This little formula is a **neuron**.

[[fig:neuron|A single neuron: multiply each input by its weight, add them up, add the bias. Training means finding good values for w1, w2 and b.]]

The data was generated from the hidden rule `5 × study + 3 × sleep + 4` **plus some random noise** (real data is never perfect). The model doesn't know the rule — it must discover numbers close to 5, 3 and 4.

## 2.3 Learning = nudging the weights with the error %%GOOD%%

Start with random weights, say `w1 = 15, w2 = 2, b = 1` (Rohit's whiteboard example). For a student with study = 3, sleep = 2 and real marks = 25:

1. **Predict:** 15×3 + 2×2 + 1 = **50**.
2. **Error** = actual − predicted = 25 − 50 = **−25** (we guessed too high).
3. **Nudge** every weight a little in the direction that reduces the error, using a small **learning rate** `lr = 0.01`:

| Update rule | Calculation | New value |
|---|---|---|
| `w1 = w1 + lr × error × study` | 15 + 0.01 × (−25) × 3 | **14.25** |
| `w2 = w2 + lr × error × sleep` | 2 + 0.01 × (−25) × 2 | **1.5** |
| `b = b + lr × error` | 1 + 0.01 × (−25) | **0.75** |

Now the prediction for the same student is 14.25×3 + 1.5×2 + 0.75 = 46.5 — closer to 25. Repeat this for every student, many times, and the weights **slide** towards the best values. This is **gradient descent**.

Why multiply by the input? An input that was **large** contributed more to the wrong answer, so its weight gets more of the blame. Mathematically, `error × input` is (up to a constant) the **slope of the squared error** with respect to that weight — the gradient — and we step downhill.

:::day Lecture27and28/first.cpp
The whole training program. You can compile it with `g++ first.cpp -o first` and run `./first` in the same folder as `dataset.csv`.
:::

```cpp title="Lecture27and28/first.cpp (the core, lightly condensed)" lines
double predict(double study, double sleep,
               double w1,    double w2, double b) {
    return w1 * study + w2 * sleep + b;
}

void train(vector<Example>& data, int epochs, double lr) {
    double w1 = 10.0, w2 = 5.0, b = 6.0;          // starting guess

    for (int epoch = 1; epoch <= epochs; epoch++) {
        for (auto& e : data) {
            double predicted = predict(e.study, e.sleep, w1, w2, b);
            double error = e.marks - predicted;
            w1 = w1 + lr * e.study * error;
            w2 = w2 + lr * e.sleep * error;
            b  = b  + lr * 1       * error;
        }
        if (epoch % 100 == 0)
            cout << "Epoch " << epoch << "  |  w1=" << w1
                 << "  w2=" << w2 << "  b=" << b << endl;
    }
}
// main(): loads dataset.csv, then calls train(data, 1000, 0.0001);
```

- **Lines 1–4** — the neuron. It's just the formula.
- **Line 7** — the starting weights (a guess; real networks start with small random numbers).
- **Line 9** — an **epoch** = one full pass over all 1000 examples. We do 1000 epochs.
- **Lines 10–16** — for **each** example: predict, compute the error, nudge all three numbers. Updating after every single example is called **stochastic gradient descent (SGD)**.
- The dataset loader (not shown) is plain C++ you know: `ifstream`, `getline`, `stringstream`, `stod`, `push_back` into a `vector<Example>`.

I compiled and ran it. The real output:

```output title="./first  (lr = 0.0001, 1000 epochs)"
Dataset loaded: 1000 examples
Epoch 100  |  w1=4.9059  w2=2.93011  b=5.03639
Epoch 200  |  w1=4.91583  w2=2.93965  b=4.91456
...                                   #> epochs 300–900 cut to save space
Epoch 1000  |  w1=4.92057  w2=2.9442  b=4.85644

==============================
Training Complete!
Learned  →  w1=4.92057  w2=2.9442  b=4.85644
Expected →  w1=5  w2=3  b=4
```

It found **4.92, 2.94, 4.86** — very close to the hidden 5, 3, 4. Not exact, because of the random noise in the data (and that is fine: we want the best fit to real data, not a perfect formula).

### Learning rate: the most important knob

I also ran the same program with other learning rates:

| Learning rate | What happened | Lesson |
|---|---|---|
| `0.000001` | After 1000 epochs still far off (w1 = 4.88, b = 5.36) | Too small → learning is painfully **slow** |
| `0.0001` | Converged to 4.92 / 2.94 / 4.86 | Good |
| `0.05` | Weights became `-nan` | Too big → each step **overshoots**, the error explodes (**diverges**) |

### Training vs inference

`trained.cpp` just **uses** the learned numbers — no more learning:

```cpp title="Lecture27and28/trained.cpp"
double predict(double study, double sleep) {
    double w1 = 4.92057;   // weights copied from the training output
    double w2 = 2.9442;
    double b  = 4.85644;
    return w1 * study + w2 * sleep + b;
}
```

```output title="./trained"
Enter study hours: 3
Enter sleep hours: 8
Predicted marks: 43.1717
```

- **Training** = finding the weights (slow, expensive, done once). Training a big LLM takes thousands of GPUs for weeks.
- **Inference** = using the weights to answer (fast, done millions of times). When you call the Gemini API, you are doing **inference** on weights Google already trained.

:::cpp The model file is just saved numbers
`trained.cpp` hard-codes three `double`s. A "7B model" is the same idea with **7 billion** numbers stored in a file. Loading a model = reading those numbers into memory; running it = lots of multiply-and-add, which is why GPUs (thousands of tiny parallel multipliers) matter.
:::

## 2.4 Why stacking lines is still a line %%GOOD%%

Lecture 29 asks: what if one neuron feeds another? Neuron 1 gives `y = w1·x + b1`; neuron 2 gives `out = w2·y + b2`. Substitute:

`out = w2·(w1·x + b1) + b2 = (w2·w1)·x + (w2·b1 + b2) = m·x + c`

Still a straight line! A hundred linear layers are no better than one. Straight lines can't describe curves like "extra pay starts only after 3 hours of overtime" or "marks stop increasing after 30".

## 2.5 ReLU: the bend that makes networks powerful %%GOOD%%

The fix is an **activation function** after each neuron. The most popular one is **ReLU**:

`ReLU(x) = max(0, x)` → negative values become 0, positive values pass through.

ReLU is a line with **one bend**. Adding bent lines builds shapes:

- Extra pay = 0 for the first 3 hours, then 1 per hour → `ReLU(x − 3)`.
- A ramp that rises between 10 and 30 and then stays flat (at 20) → `ReLU(x − 10) − ReLU(x − 30)`.
- Lecture 30's magic: `y = x²` at whole numbers is **exactly** `ReLU(x) + 2·ReLU(x−1) + 2·ReLU(x−2) + 2·ReLU(x−3) + …` (each new ReLU increases the slope by 2 — the gaps 1, 3, 5, 7… between squares). And `y = x³` = `ReLU(x) + 6·ReLU(x−1) + 12·ReLU(x−2) + 18·ReLU(x−3) + …`. I checked both formulas for x = 0…7.

[[fig:relu-sum|Left: ReLU is a line with one bend; two ReLUs make a ramp that saturates. Right: many small bends follow the curve y = x².]]

> With **enough neurons and a bend (activation) after each**, a network can approximate almost any function. That's the intuition behind the **universal approximation theorem**, and it's why deep learning works.

Other activations you may hear: **sigmoid** (squashes to 0…1), **tanh** (−1…1), **GELU**/**SwiGLU** (smooth ReLU-like; used inside modern LLMs). The final layer of an LLM uses **softmax** to turn scores into probabilities that add up to 1.

## 2.6 From one neuron to an LLM (the 3-page version) %%GOOD%%

**Neural network** = layers of neurons. Each layer: multiply by a weight matrix, add bias, apply activation. **Deep** = many layers.

**Backpropagation** = the chain rule from calculus, used to compute how much **each** weight in **every** layer contributed to the error, so gradient descent can nudge all of them — exactly like `w1 += lr × error × study`, but for billions of weights at once.

An LLM is a big network with a special design called the **Transformer** (2017, "Attention Is All You Need"):

[[fig:transformer-mini|A decoder-only transformer (the GPT/Gemini family) in one picture.]]

1. **Tokenise** — text → token ids (Chapter 1).
2. **Embed** — each id becomes a vector of numbers (an **embedding**; Chapter 6 is all about these), plus information about its **position**.
3. **Transformer blocks** (dozens of them), each with:
    - **Self-attention** — every token looks at the tokens before it and decides **how much each one matters** to it. In "The cat sat because **it** was tired", attention lets "it" pull information from "cat".
    - **Feed-forward network** — a normal neural network (with a GELU-style activation) applied to each token.
4. **Output** — the last vector becomes a score for every token in the vocabulary → **softmax** → probabilities → pick the next token (Chapter 1).

**Attention in one line**: each token makes a **query** ("what am I looking for?"), every earlier token offers a **key** ("what do I contain?") and a **value** ("what information do I pass on?"). Score = how well query matches key (a dot product, scaled), softmax turns scores into weights, and the output is the weighted sum of values. A **causal mask** stops a token from looking at future tokens — the model must predict them.

Why transformers won: older **RNNs** read text one token at a time (slow, forget long-range context). Attention looks at all positions **in parallel** during training, which fits GPUs perfectly and handles long-range links.

**How chat models are made** (three stages):

| Stage | What it learns | Data |
|---|---|---|
| **Pre-training** | Language and world knowledge by next-token prediction | Trillions of tokens of web, books, code |
| **Instruction tuning (SFT)** | To follow instructions and answer like an assistant | Curated question → good answer pairs |
| **Preference tuning (RLHF / DPO)** | To prefer helpful, honest, safe answers | Humans (or models) ranking answers |

## 2.7 Prompting vs RAG vs fine-tuning %%MUST%%

A classic interview question: *"Your LLM doesn't know our company's data. What do you do?"*

| Approach | What changes | Best for | Weak at |
|---|---|---|---|
| **Prompt engineering** | Only the input text | Format, tone, simple rules, few examples | Large or changing knowledge |
| **RAG** (Chapter 8) | Relevant data is **retrieved** and put in the prompt | Fresh, private, large knowledge; **citations**; access control | Tasks needing new *skills* or style |
| **Fine-tuning** | The model's **weights** (usually a small **LoRA** adapter) | A consistent style/format, domain language, a narrow skill, a smaller cheaper model | Adding facts that change (retrain every time), citations |

Rule of thumb: **try prompting first, add RAG for knowledge, fine-tune for behaviour.** **LoRA** (Low-Rank Adaptation) freezes the original weights and trains two small matrices per layer, so fine-tuning fits on one GPU and the adapter file is tiny. They are often combined: a fine-tuned model that is also given retrieved context.

:::remember
- ML = learn the function from examples when you can't write the rules.
- Neuron = `w·x + b`; training = **predict → error → nudge weights** (`w += lr × error × input`) = **gradient descent**.
- **Epoch** = one pass over the data. **Learning rate**: too small = slow, too big = diverges (`nan`).
- **Training** finds weights (expensive, once); **inference** uses them (every API call).
- Stacked linear layers = still linear. **Activations** (ReLU = `max(0, x)`) add bends; many bends approximate any curve.
- LLM = tokens → embeddings → transformer blocks (**self-attention** + feed-forward) → softmax over the vocabulary.
- Pre-training → instruction tuning → preference tuning (RLHF/DPO).
- **Prompt first, RAG for knowledge, fine-tune (LoRA) for behaviour.**
:::

:::quiz
1. With `w1 = 15, w2 = 2, b = 1`, lr = 0.01, and a student (study 3, sleep 2, marks 25), what is the new `b`?
2. The training output shows `w1 = -nan`. What most likely went wrong?
3. Why is a network with 10 linear layers and no activation no better than one neuron?
4. Write `y = x²` (for whole numbers) using ReLUs.
5. Your company's policy documents change every week. RAG or fine-tuning? Why?
:::

:::answer
1. Error = 25 − 50 = −25, so `b = 1 + 0.01 × (−25) = 0.75`.
2. The learning rate is too big: the updates overshoot and grow until they overflow (`0.05` does this on the course dataset).
3. Composing linear functions gives another linear function (`w2(w1x + b1) + b2 = mx + c`).
4. `ReLU(x) + 2·ReLU(x−1) + 2·ReLU(x−2) + 2·ReLU(x−3) + …`
5. **RAG** — re-index the new documents; no retraining, and you can cite the exact document. Fine-tuning would need retraining every week and still can't cite sources.
:::

:::qa Interview questions — ML and transformer basics
Q: What is gradient descent?
An optimisation method: compute how the error changes when each weight changes (the gradient), then move every weight a small step (the learning rate) in the direction that lowers the error. Repeat over the data for many epochs. In the course's C++ example the update is `w += lr × error × input`.

Q: What is the role of an activation function?
To add non-linearity. Without it, any stack of layers collapses into one linear function. ReLU (`max(0, x)`) is cheap and works well; modern LLMs use smooth variants like GELU or SwiGLU.

Q: Explain self-attention simply.
Each token builds a query; every earlier token has a key and a value. The query–key similarity (scaled dot product, then softmax) says how much to "attend" to each token, and the output is the weighted mix of their values. It lets a word like "it" pull meaning from "the cat" several words back, and it runs in parallel on GPUs.

Q: What is the difference between training and inference?
Training adjusts the weights using data and gradients — expensive, done once or rarely. Inference runs the fixed weights to produce outputs — what every API call does. Costs, hardware and latency concerns are different for each.

Q: When would you fine-tune instead of using RAG?
When I need to change behaviour rather than add knowledge: a strict output format, a domain's writing style, a narrow classification skill, or distilling a big model's behaviour into a smaller, cheaper one. For facts that change, or when I need citations, I use RAG. Often both are combined. With LoRA, fine-tuning trains a small adapter instead of all weights.

Q: What is LoRA?
Low-Rank Adaptation: freeze the pretrained weights and learn two small low-rank matrices per layer whose product is added to the original weights. It cuts memory and cost dramatically and produces a small adapter file you can swap in and out.
:::
