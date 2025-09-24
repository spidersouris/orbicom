# orbicom

Repository for the **Cohésion textuelle dans les textes générés par les SLM : expressions référentielles et genre** paper presented at the [Orbicom – ITI LiRiC CIAREI Congress](https://orbicom-2025.sciencesconf.org/?lang=en) (Communication, artificial intelligence, remediation, ethics and inclusion) held in Strasbourg, France from September 29th to October 1st, 2025.

## Generating with log probabilities

```
usage: generate.py [-h] -l {ce1,cm1} -t {literature,scientific} -g {continuation,generation} -m MODEL_ID [-k TOP_K] [-tk MAX_NEW_TOKENS]
```

---

```
options:
  -l {ce1,cm1}, --level {ce1,cm1}
                        Level of the corpus ('ce1' or 'cm1')
  -t {literature,scientific}, --text_type {literature,scientific}
                        Type of text from the corpus ('literature' or 'scientific')
  -g {continuation,generation}, --gen_type {continuation,generation}
                        Type of generation ('continuation' or 'generation')
  -m MODEL_ID, --model_id MODEL_ID
                        Model identifier
  -k TOP_K, --top_k TOP_K
                        Number of top-k alternatives to consider for logprobs (default: 30)
  -tk MAX_NEW_TOKENS, --max_new_tokens MAX_NEW_TOKENS
                        Maximum number of new tokens to generate (default: 512)
```

## Plotting

```
usage: plot.py [-h] -m MODELS [MODELS ...] -l {ce1,cm1,all} -t {literature,scientific,all} -g {continuation,generation,all} [-r MIN_RATIO] [-k TOP_K_LIMIT] [-c CONTEXT_WINDOW] [-s SURPRISAL_THRESHOLD] [--lang {fr,en}] [-svg] [-html] token1 token2
```

---

```
positional arguments:
  token1                First token to analyze
  token2                Second token to analyze

options:
  -m MODELS [MODELS ...], --models MODELS [MODELS ...]
                        List of model identifiers to include in the plot (default: all models; can be "llama", "qwen", "mistral")
  -l {ce1,cm1,all}, --level {ce1,cm1,all}
                        Level of the corpus ('ce1' or 'cm1' or 'all' for both levels)
  -t {literature,scientific,all}, --text_type {literature,scientific,all}
                        Type of text from the corpus ('literature' or 'scientific' or 'all' for both types)
  -g {continuation,generation,all}, --gen_type {continuation,generation,all}
                        Type of generation ('continuation', 'generation', or 'all' for both types)
  -r MIN_RATIO, --min_ratio MIN_RATIO
                        (probs/surprisal) Minimum ratio of value to key probability for inclusion in the plot (default: 1/3)
  -k TOP_K_LIMIT, --top_k_limit TOP_K_LIMIT
                        (probs) Limit for top-k alternatives. If None, no limit is applied (default: None)
  -c CONTEXT_WINDOW, --context_window CONTEXT_WINDOW
                        (surprisal, HTML) Context window size of preceding tokens (default: 20)
  -s SURPRISAL_THRESHOLD, --surprisal_threshold SURPRISAL_THRESHOLD
                        (surprisal) Surprisal threshold for filtering (default: 4.0)
  --lang {fr,en}        Language of the plots (default: 'fr')
  -svg, --save_svg      Save plot as SVG
  -html, --save_html    (surprisal) Save an interactive HTML plot
```

For example, the following line will plot taking into account literature texts (`-t literature`) from any level (`-l all`) and any generation type (`-g all`), with a top-k limit of 30 (`-k 30`). The plots will be saved in English (`--lang en`) as SVG (`-svg`), and an interactive HTML plot will be saved for the surprisal plot (`-html`).

`python plot.py il elle -l all -t literature -g all -k 30 --lang en -svg -html`
