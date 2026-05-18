---
tags:
- sentence-transformers
- cross-encoder
- reranker
- generated_from_trainer
- dataset_size:210725
- loss:BinaryCrossEntropyLoss
base_model: cross-encoder/ms-marco-MiniLM-L2-v2
pipeline_tag: text-ranking
library_name: sentence-transformers
---

# CrossEncoder based on cross-encoder/ms-marco-MiniLM-L2-v2

This is a [Cross Encoder](https://www.sbert.net/docs/cross_encoder/usage/usage.html) model finetuned from [cross-encoder/ms-marco-MiniLM-L2-v2](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L2-v2) using the [sentence-transformers](https://www.SBERT.net) library. It computes scores for pairs of texts, which can be used for text reranking and semantic search.

## Model Details

### Model Description
- **Model Type:** Cross Encoder
- **Base model:** [cross-encoder/ms-marco-MiniLM-L2-v2](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L2-v2) <!-- at revision 1b5cd67b15209f24824c50370e0397743aa9b787 -->
- **Maximum Sequence Length:** 160 tokens
- **Number of Output Labels:** 1 label
- **Supported Modality:** Text
<!-- - **Training Dataset:** Unknown -->
<!-- - **Language:** Unknown -->
<!-- - **License:** Unknown -->

### Model Sources

- **Documentation:** [Sentence Transformers Documentation](https://sbert.net)
- **Documentation:** [Cross Encoder Documentation](https://www.sbert.net/docs/cross_encoder/usage/usage.html)
- **Repository:** [Sentence Transformers on GitHub](https://github.com/huggingface/sentence-transformers)
- **Hugging Face:** [Cross Encoders on Hugging Face](https://huggingface.co/models?library=sentence-transformers&other=cross-encoder)

### Full Model Architecture

```
CrossEncoder(
  (0): Transformer({'transformer_task': 'sequence-classification', 'modality_config': {'text': {'method': 'forward', 'method_output_name': 'logits'}}, 'module_output_name': 'scores', 'architecture': 'BertForSequenceClassification'})
)
```

## Usage

### Direct Usage (Sentence Transformers)

First install the Sentence Transformers library:

```bash
pip install -U sentence-transformers
```

Then you can load this model and run inference.
```python
from sentence_transformers import CrossEncoder

# Download from the 🤗 Hub
model = CrossEncoder("cross_encoder_model_id")
# Get scores for pairs of inputs
pairs = [
    ['lemma injective_not_constant:\n  fixes S :: "\'a::{perfect_space} set"\n  shows "\\<lbrakk>open S; inj_on f S; f constant_on S\\<rbrakk> \\<Longrightarrow> S = {}"', 'on_circline_moebius_circline_I: fixes H :: "circline"   and z :: "complex_homo"   and M :: "moebius" assumes "on_circline H z" shows "on_circline (moebius_circline M H) (moebius_pt M z)"'],
    ['1. hmset_pos (A + B) =\n    hmset_pos A - hmset_neg B + (hmset_pos B - hmset_neg A)', 'diff_right_commute: fixes a :: "\'a"   and c :: "\'a"   and b :: "\'a" shows "a - c - b = a - b - c"'],
    ['1. inverse (fls_X ^ n) = fls_X_inv ^ n', 'add: fixes f :: "\'a \\<Rightarrow> \'b"   and x :: "\'a"   and y :: "\'a" assumes "Modules.additive f" shows "f (x + y) = f x + f y"'],
    ['1. \\<delta>1 \\<inter># \\<delta>2 = {#}', 'simps: fixes p :: "rat poly"   and xs :: "rat list"   and fs :: "rat poly list" shows "factorize_root_free_main p xs fs = (case xs of [] \\<Rightarrow> let l = lead_coeff p; q = smult (inverse l) p in (l, if q = 1 then fs else q # fs) | x # xs \\<Rightarrow> if poly p x = 0 then factorize_root_free_main (p div [:- x, 1:]) (x # xs) ([:- x, 1:] # fs) else factorize_root_free_main p xs fs)"'],
    ['1. correct ((recf.Id m n, xs, []) # rest, None)', 'Neg_Forall_in_extend: fixes S :: "(nat, \'a) form set"   and C :: "(nat, \'a) form set set"   and f :: "nat \\<Rightarrow> (nat, \'a) form"   and n :: "nat"   and P :: "(nat, \'a) form" assumes "extend S C f n \\<union> {f n} \\<in> C"   and "Neg (Forall P) = f n" shows "Neg (P[App (SOME k. k \\<notin> \\<Union> (params ` (extend S C f n \\<union> {f n}))) []/0]) \\<in> extend S C f (Suc n)"'],
]
scores = model.predict(pairs)
print(scores)
# [-7.332   6.4703  7.9048 -7.0904 -6.2759]

# Or rank different texts based on similarity to a single text
ranks = model.rank(
    'lemma injective_not_constant:\n  fixes S :: "\'a::{perfect_space} set"\n  shows "\\<lbrakk>open S; inj_on f S; f constant_on S\\<rbrakk> \\<Longrightarrow> S = {}"',
    [
        'on_circline_moebius_circline_I: fixes H :: "circline"   and z :: "complex_homo"   and M :: "moebius" assumes "on_circline H z" shows "on_circline (moebius_circline M H) (moebius_pt M z)"',
        'diff_right_commute: fixes a :: "\'a"   and c :: "\'a"   and b :: "\'a" shows "a - c - b = a - b - c"',
        'add: fixes f :: "\'a \\<Rightarrow> \'b"   and x :: "\'a"   and y :: "\'a" assumes "Modules.additive f" shows "f (x + y) = f x + f y"',
        'simps: fixes p :: "rat poly"   and xs :: "rat list"   and fs :: "rat poly list" shows "factorize_root_free_main p xs fs = (case xs of [] \\<Rightarrow> let l = lead_coeff p; q = smult (inverse l) p in (l, if q = 1 then fs else q # fs) | x # xs \\<Rightarrow> if poly p x = 0 then factorize_root_free_main (p div [:- x, 1:]) (x # xs) ([:- x, 1:] # fs) else factorize_root_free_main p xs fs)"',
        'Neg_Forall_in_extend: fixes S :: "(nat, \'a) form set"   and C :: "(nat, \'a) form set set"   and f :: "nat \\<Rightarrow> (nat, \'a) form"   and n :: "nat"   and P :: "(nat, \'a) form" assumes "extend S C f n \\<union> {f n} \\<in> C"   and "Neg (Forall P) = f n" shows "Neg (P[App (SOME k. k \\<notin> \\<Union> (params ` (extend S C f n \\<union> {f n}))) []/0]) \\<in> extend S C f (Suc n)"',
    ]
)
# [{'corpus_id': ..., 'score': ...}, {'corpus_id': ..., 'score': ...}, ...]
```

<!--
### Direct Usage (Transformers)

<details><summary>Click to see the direct usage in Transformers</summary>

</details>
-->

<!--
### Downstream Usage (Sentence Transformers)

You can finetune this model on your own dataset.

<details><summary>Click to expand</summary>

</details>
-->

<!--
### Out-of-Scope Use

*List how the model may foreseeably be misused and address what users ought not to do with the model.*
-->

<!--
## Bias, Risks and Limitations

*What are the known or foreseeable issues stemming from this model? You could also flag here known failure cases or weaknesses of the model.*
-->

<!--
### Recommendations

*What are recommendations with respect to the foreseeable issues? For example, filtering explicit content.*
-->

## Training Details

### Training Dataset

#### Unnamed Dataset

* Size: 210,725 training samples
* Columns: <code>sentence_0</code>, <code>sentence_1</code>, and <code>label</code>
* Approximate statistics based on the first 100 samples:
  |          | sentence_0                                                                         | sentence_1                                                                         | label                                                          |
  |:---------|:-----------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------|:---------------------------------------------------------------|
  | type     | string                                                                             | string                                                                             | float                                                          |
  | modality | text                                                                               | text                                                                               |                                                                |
  | details  | <ul><li>min: 5 tokens</li><li>mean: 56.02 tokens</li><li>max: 160 tokens</li></ul> | <ul><li>min: 10 tokens</li><li>mean: 79.2 tokens</li><li>max: 160 tokens</li></ul> | <ul><li>min: 0.0</li><li>mean: 0.22</li><li>max: 1.0</li></ul> |
* Samples:
  | sentence_0                                                                                                                                                                       | sentence_1                                                                                                                                                                                              | label            |
  |:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------|
  | <code>lemma injective_not_constant:<br>  fixes S :: "'a::{perfect_space} set"<br>  shows "\<lbrakk>open S; inj_on f S; f constant_on S\<rbrakk> \<Longrightarrow> S = {}"</code> | <code>on_circline_moebius_circline_I: fixes H :: "circline"   and z :: "complex_homo"   and M :: "moebius" assumes "on_circline H z" shows "on_circline (moebius_circline M H) (moebius_pt M z)"</code> | <code>0.0</code> |
  | <code>1. hmset_pos (A + B) =<br>    hmset_pos A - hmset_neg B + (hmset_pos B - hmset_neg A)</code>                                                                               | <code>diff_right_commute: fixes a :: "'a"   and c :: "'a"   and b :: "'a" shows "a - c - b = a - b - c"</code>                                                                                          | <code>0.0</code> |
  | <code>1. inverse (fls_X ^ n) = fls_X_inv ^ n</code>                                                                                                                              | <code>add: fixes f :: "'a \<Rightarrow> 'b"   and x :: "'a"   and y :: "'a" assumes "Modules.additive f" shows "f (x + y) = f x + f y"</code>                                                           | <code>1.0</code> |
* Loss: [<code>BinaryCrossEntropyLoss</code>](https://sbert.net/docs/package_reference/cross_encoder/losses.html#binarycrossentropyloss) with these parameters:
  ```json
  {
      "activation_fn": "torch.nn.modules.linear.Identity",
      "pos_weight": null
  }
  ```

### Training Hyperparameters
#### Non-Default Hyperparameters

- `per_device_train_batch_size`: 4
- `per_device_eval_batch_size`: 4
- `num_train_epochs`: 1

#### All Hyperparameters
<details><summary>Click to expand</summary>

- `do_predict`: False
- `prediction_loss_only`: True
- `per_device_train_batch_size`: 4
- `per_device_eval_batch_size`: 4
- `gradient_accumulation_steps`: 1
- `eval_accumulation_steps`: None
- `torch_empty_cache_steps`: None
- `learning_rate`: 5e-05
- `weight_decay`: 0.0
- `adam_beta1`: 0.9
- `adam_beta2`: 0.999
- `adam_epsilon`: 1e-08
- `max_grad_norm`: 1
- `num_train_epochs`: 1
- `max_steps`: -1
- `lr_scheduler_type`: linear
- `lr_scheduler_kwargs`: None
- `warmup_ratio`: None
- `warmup_steps`: 0
- `log_level`: passive
- `log_level_replica`: warning
- `log_on_each_node`: True
- `logging_nan_inf_filter`: True
- `enable_jit_checkpoint`: False
- `save_on_each_node`: False
- `save_only_model`: False
- `restore_callback_states_from_checkpoint`: False
- `use_cpu`: False
- `seed`: 42
- `data_seed`: None
- `bf16`: False
- `fp16`: False
- `bf16_full_eval`: False
- `fp16_full_eval`: False
- `tf32`: None
- `local_rank`: -1
- `ddp_backend`: None
- `debug`: []
- `dataloader_drop_last`: False
- `dataloader_num_workers`: 0
- `dataloader_prefetch_factor`: None
- `disable_tqdm`: False
- `remove_unused_columns`: True
- `label_names`: None
- `load_best_model_at_end`: False
- `ignore_data_skip`: False
- `fsdp`: []
- `fsdp_config`: {'min_num_params': 0, 'xla': False, 'xla_fsdp_v2': False, 'xla_fsdp_grad_ckpt': False}
- `accelerator_config`: {'split_batches': False, 'dispatch_batches': None, 'even_batches': True, 'use_seedable_sampler': True, 'non_blocking': False, 'gradient_accumulation_kwargs': None}
- `parallelism_config`: None
- `deepspeed`: None
- `label_smoothing_factor`: 0.0
- `optim`: adamw_torch_fused
- `optim_args`: None
- `group_by_length`: False
- `length_column_name`: length
- `project`: huggingface
- `trackio_space_id`: trackio
- `ddp_find_unused_parameters`: None
- `ddp_bucket_cap_mb`: None
- `ddp_broadcast_buffers`: False
- `dataloader_pin_memory`: True
- `dataloader_persistent_workers`: False
- `skip_memory_metrics`: True
- `push_to_hub`: False
- `resume_from_checkpoint`: None
- `hub_model_id`: None
- `hub_strategy`: every_save
- `hub_private_repo`: None
- `hub_always_push`: False
- `hub_revision`: None
- `gradient_checkpointing`: False
- `gradient_checkpointing_kwargs`: None
- `include_for_metrics`: []
- `eval_do_concat_batches`: True
- `auto_find_batch_size`: False
- `full_determinism`: False
- `ddp_timeout`: 1800
- `torch_compile`: False
- `torch_compile_backend`: None
- `torch_compile_mode`: None
- `include_num_input_tokens_seen`: no
- `neftune_noise_alpha`: None
- `optim_target_modules`: None
- `batch_eval_metrics`: False
- `eval_on_start`: False
- `use_liger_kernel`: False
- `liger_kernel_config`: None
- `eval_use_gather_object`: False
- `average_tokens_across_devices`: True
- `use_cache`: False
- `prompts`: None
- `batch_sampler`: batch_sampler
- `multi_dataset_batch_sampler`: proportional
- `router_mapping`: {}
- `learning_rate_mapping`: {}

</details>

### Training Logs
<details><summary>Click to expand</summary>

| Epoch  | Step  | Training Loss |
|:------:|:-----:|:-------------:|
| 0.0095 | 500   | 1.0491        |
| 0.0190 | 1000  | 0.7661        |
| 0.0285 | 1500  | 0.6449        |
| 0.0380 | 2000  | 0.5605        |
| 0.0475 | 2500  | 0.5601        |
| 0.0569 | 3000  | 0.4810        |
| 0.0664 | 3500  | 0.4844        |
| 0.0759 | 4000  | 0.4731        |
| 0.0854 | 4500  | 0.4667        |
| 0.0949 | 5000  | 0.4304        |
| 0.1044 | 5500  | 0.4313        |
| 0.1139 | 6000  | 0.3340        |
| 0.1234 | 6500  | 0.4035        |
| 0.1329 | 7000  | 0.3905        |
| 0.1424 | 7500  | 0.3578        |
| 0.1519 | 8000  | 0.3349        |
| 0.1613 | 8500  | 0.3458        |
| 0.1708 | 9000  | 0.3209        |
| 0.1803 | 9500  | 0.3465        |
| 0.1898 | 10000 | 0.3304        |
| 0.1993 | 10500 | 0.3295        |
| 0.2088 | 11000 | 0.3223        |
| 0.2183 | 11500 | 0.3268        |
| 0.2278 | 12000 | 0.3237        |
| 0.2373 | 12500 | 0.3393        |
| 0.2468 | 13000 | 0.3016        |
| 0.2563 | 13500 | 0.3593        |
| 0.2657 | 14000 | 0.3024        |
| 0.2752 | 14500 | 0.3217        |
| 0.2847 | 15000 | 0.3156        |
| 0.2942 | 15500 | 0.2628        |
| 0.3037 | 16000 | 0.3263        |
| 0.3132 | 16500 | 0.3005        |
| 0.3227 | 17000 | 0.2594        |
| 0.3322 | 17500 | 0.2911        |
| 0.3417 | 18000 | 0.2867        |
| 0.3512 | 18500 | 0.3033        |
| 0.3607 | 19000 | 0.3014        |
| 0.3701 | 19500 | 0.2725        |
| 0.3796 | 20000 | 0.2836        |
| 0.3891 | 20500 | 0.2634        |
| 0.3986 | 21000 | 0.2751        |
| 0.4081 | 21500 | 0.2806        |
| 0.4176 | 22000 | 0.2886        |
| 0.4271 | 22500 | 0.2609        |
| 0.4366 | 23000 | 0.2869        |
| 0.4461 | 23500 | 0.2846        |
| 0.4556 | 24000 | 0.2718        |
| 0.4651 | 24500 | 0.2655        |
| 0.4745 | 25000 | 0.2558        |
| 0.4840 | 25500 | 0.2784        |
| 0.4935 | 26000 | 0.2543        |
| 0.5030 | 26500 | 0.2961        |
| 0.5125 | 27000 | 0.2807        |
| 0.5220 | 27500 | 0.2877        |
| 0.5315 | 28000 | 0.2734        |
| 0.5410 | 28500 | 0.2650        |
| 0.5505 | 29000 | 0.2682        |
| 0.5600 | 29500 | 0.2710        |
| 0.5695 | 30000 | 0.2832        |
| 0.5789 | 30500 | 0.2551        |
| 0.5884 | 31000 | 0.2433        |
| 0.5979 | 31500 | 0.2427        |
| 0.6074 | 32000 | 0.2604        |
| 0.6169 | 32500 | 0.2868        |
| 0.6264 | 33000 | 0.2252        |
| 0.6359 | 33500 | 0.2642        |
| 0.6454 | 34000 | 0.2358        |
| 0.6549 | 34500 | 0.2693        |
| 0.6644 | 35000 | 0.2247        |
| 0.6739 | 35500 | 0.2501        |
| 0.6833 | 36000 | 0.2926        |
| 0.6928 | 36500 | 0.2007        |
| 0.7023 | 37000 | 0.2215        |
| 0.7118 | 37500 | 0.2282        |
| 0.7213 | 38000 | 0.2686        |
| 0.7308 | 38500 | 0.2357        |
| 0.7403 | 39000 | 0.2560        |
| 0.7498 | 39500 | 0.2547        |
| 0.7593 | 40000 | 0.2289        |
| 0.7688 | 40500 | 0.2270        |
| 0.7783 | 41000 | 0.2419        |
| 0.7877 | 41500 | 0.2331        |
| 0.7972 | 42000 | 0.2173        |
| 0.8067 | 42500 | 0.2507        |
| 0.8162 | 43000 | 0.2504        |
| 0.8257 | 43500 | 0.2363        |
| 0.8352 | 44000 | 0.2612        |
| 0.8447 | 44500 | 0.2329        |
| 0.8542 | 45000 | 0.2349        |
| 0.8637 | 45500 | 0.2606        |
| 0.8732 | 46000 | 0.2249        |
| 0.8827 | 46500 | 0.2247        |
| 0.8921 | 47000 | 0.2110        |
| 0.9016 | 47500 | 0.2696        |
| 0.9111 | 48000 | 0.2321        |
| 0.9206 | 48500 | 0.2585        |
| 0.9301 | 49000 | 0.2441        |
| 0.9396 | 49500 | 0.2314        |
| 0.9491 | 50000 | 0.2633        |
| 0.9586 | 50500 | 0.2279        |
| 0.9681 | 51000 | 0.2564        |
| 0.9776 | 51500 | 0.2351        |
| 0.9871 | 52000 | 0.2647        |
| 0.9965 | 52500 | 0.2789        |

</details>

### Training Time
- **Training**: 16.5 minutes

### Framework Versions
- Python: 3.12.13
- Sentence Transformers: 5.5.0
- Transformers: 5.0.0
- PyTorch: 2.10.0+cu128
- Accelerate: 1.13.0
- Datasets: 4.8.5
- Tokenizers: 0.22.2

## Additional Resources

- [Training and Finetuning Reranker Models with Sentence Transformers](https://huggingface.co/blog/train-reranker): the end-to-end guide for training or finetuning Cross Encoder (reranker) models.
- [Multimodal Embedding & Reranker Models with Sentence Transformers](https://huggingface.co/blog/multimodal-sentence-transformers): use text, image, audio, and video reranker models through the same API.
- [Training and Finetuning Multimodal Embedding & Reranker Models with Sentence Transformers](https://huggingface.co/blog/train-multimodal-sentence-transformers): training multimodal Cross Encoders.

## Citation

### BibTeX

#### Sentence Transformers
```bibtex
@inproceedings{reimers-2019-sentence-bert,
    title = "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks",
    author = "Reimers, Nils and Gurevych, Iryna",
    booktitle = "Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing",
    month = "11",
    year = "2019",
    publisher = "Association for Computational Linguistics",
    url = "https://arxiv.org/abs/1908.10084",
}
```

<!--
## Glossary

*Clearly define terms in order to be accessible across audiences.*
-->

<!--
## Model Card Authors

*Lists the people who create the model card, providing recognition and accountability for the detailed work that goes into its construction.*
-->

<!--
## Model Card Contact

*Provides a way for people who have updates to the Model Card, suggestions, or questions, to contact the Model Card authors.*
-->