import argparse
import json
import os

import torch
from corpus import get_prompt, load_corpus
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
)


def load_model(model, device):
    """Load the model and tokenizer."""
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model)

    print("Loading model...")
    model = AutoModelForCausalLM.from_pretrained(
        model,
        torch_dtype=torch.float16 if device != "cpu" else torch.float32,
        device_map="auto",
    )

    return model, tokenizer


def generate_with_logprobs(
    device, model, tokenizer, prompt_id, prompt, top_k=30, max_new_tokens=512
):
    """Generate text and save logprobs for each token."""
    # tokenize input
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    input_len = inputs["input_ids"].shape[1]

    # generate text
    print(f"Generating text for prompt {prompt_id}...")
    outputs = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        do_sample=True,
        temperature=1.0,
        top_p=0.9,
        pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id,
        return_dict_in_generate=True,
        output_scores=True,
    )

    sequences = outputs.sequences
    scores = outputs.scores

    generated_ids = sequences[0][input_len:]

    results = []
    for i, (token_id, logits) in enumerate(zip(generated_ids, scores)):
        logprobs = torch.log_softmax(logits[0], dim=-1)

        token_logprob = logprobs[token_id].item()

        # get top-k alternatives
        topk_logprobs, topk_indices = torch.topk(logprobs, k=top_k)
        topk_tokens = tokenizer.convert_ids_to_tokens(topk_indices.tolist())

        top_k_list = [
            {"token": tok.replace("Ġ", ""), "logprob": lp.item()}
            for tok, lp in zip(topk_tokens, topk_logprobs)
            if lp.item() != float("-inf")
        ]

        context = tokenizer.decode(generated_ids[:i])

        results.append(
            {
                "step": i,
                "token": tokenizer.convert_ids_to_tokens([token_id])[0],
                "logprob": token_logprob,
                "top_k": top_k_list,
                "context": context,
            }
        )

    generated_text = tokenizer.decode(generated_ids, skip_special_tokens=True)

    if len(generated_text) < 20:
        print(
            f"No or but few text generated for prompt {prompt_id}, redoing generation"
        )
        return generate_with_logprobs(
            model, tokenizer, prompt_id, prompt, top_k, max_new_tokens
        )

    model_id_str = model_id.split("/")[1]

    if not os.path.exists(f"results/{model_id_str}/{level}/logits"):
        os.makedirs(f"results/{model_id_str}/{level}/logits")

    if not os.path.exists(f"results/{model_id_str}/{level}/gen"):
        os.makedirs(f"results/{model_id_str}/{level}/gen")

    with open(
        f"results/{model_id_str}/{level}/logits/token_logits_{model_id_str}_{prompt_id}_{text_type}_{gen_type}.jsonl",
        "w",
        encoding="utf-8",
    ) as f:
        for res in results:
            f.write(json.dumps(res, ensure_ascii=False) + "\n")

    with open(
        f"results/{model_id_str}/{level}/gen/generated_text_{model_id_str}_{prompt_id}_{text_type}_{gen_type}.txt",
        "w",
        encoding="utf-8",
    ) as f:
        f.write(generated_text)


def main(level, text_type, gen_type, model_id, top_k=30, max_new_tokens=512):
    corpus = load_corpus(
        level, text_type, extract=True if gen_type == "continuation" else False
    )

    prompts = {}

    for text_id, content in corpus.items():
        prompts[text_id] = get_prompt(gen_type, text_type, level, content)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    model, tokenizer = load_model(model_id, device)

    for k, v in prompts.items():
        print(
            f"Generating with prompt {k}, level {level}, text_type {text_type}, gen_type {gen_type}"
        )
        generate_with_logprobs(device, model, tokenizer, k, v, top_k, max_new_tokens)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate text with logprobs")
    parser.add_argument(
        "-l",
        "--level",
        type=str,
        choices=["ce1", "cm1"],
        required=True,
        help="Level of the corpus ('ce1' or 'cm1')",
    )
    parser.add_argument(
        "-t",
        "--text_type",
        type=str,
        choices=["literature", "scientific"],
        required=True,
        help="Type of text from the corpus ('literature' or 'scientific')",
    )
    parser.add_argument(
        "-g",
        "--gen_type",
        type=str,
        choices=["continuation", "generation"],
        required=True,
        help="Type of generation ('continuation' or 'generation')",
    )
    parser.add_argument(
        "-m", "--model_id", type=str, required=True, help="Model identifier"
    )
    parser.add_argument(
        "-k",
        "--top_k",
        type=int,
        default=30,
        help="Number of top-k alternatives to consider for logprobs (default: 30)",
    )
    parser.add_argument(
        "-tk",
        "--max_new_tokens",
        type=int,
        default=512,
        help="Maximum number of new tokens to generate (default: 512)",
    )

    args = parser.parse_args()

    level = args.level
    text_type = args.text_type
    gen_type = args.gen_type
    top_k = args.top_k
    max_new_tokens = args.max_new_tokens
    model_id = args.model_id

    main(level, text_type, gen_type, model_id, top_k, max_new_tokens)
