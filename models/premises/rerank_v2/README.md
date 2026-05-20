---
tags:
- sentence-transformers
- cross-encoder
- reranker
- generated_from_trainer
- dataset_size:78285
- loss:BinaryCrossEntropyLoss
pipeline_tag: text-ranking
library_name: sentence-transformers
metrics:
- accuracy
- accuracy_threshold
- f1
- f1_threshold
- precision
- recall
- average_precision
model-index:
- name: CrossEncoder
  results:
  - task:
      type: cross-encoder-binary-classification
      name: Cross Encoder Binary Classification
    dataset:
      name: afp aug val
      type: afp_aug_val
    metrics:
    - type: accuracy
      value: 0.8406713415335096
      name: Accuracy
    - type: accuracy_threshold
      value: -0.5008544921875
      name: Accuracy Threshold
    - type: f1
      value: 0.6214986832655015
      name: F1
    - type: f1_threshold
      value: -1.162109375
      name: F1 Threshold
    - type: precision
      value: 0.6735858847950181
      name: Precision
    - type: recall
      value: 0.5768888888888889
      name: Recall
    - type: average_precision
      value: 0.7157927748538151
      name: Average Precision
---

# CrossEncoder

This is a [Cross Encoder](https://www.sbert.net/docs/cross_encoder/usage/usage.html) model trained using the [sentence-transformers](https://www.SBERT.net) library. It computes scores for pairs of texts, which can be used for text reranking and semantic search.

## Model Details

### Model Description
- **Model Type:** Cross Encoder
<!-- - **Base model:** [Unknown](https://huggingface.co/unknown) -->
- **Maximum Sequence Length:** 256 tokens
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
    ['n \\<ge> 2 \\<Longrightarrow> n = fib i \\<Longrightarrow> n = fib j \\<Longrightarrow> i = j', '2 \\<le> n \\<Longrightarrow> fib i \\<le> n \\<Longrightarrow> n < fib (Suc i) \\<Longrightarrow> 2 \\<le> i'],
    ['P256_ECdomainParametersValid P256_a P256_b P256_G P256_n P256_h P256_t', 'P256_on_curve P256_a P256_b P256_G'],
    ['x \\<le> y \\<Longrightarrow> d x \\<le> d y', 'x \\<le> y \\<longleftrightarrow> (\\<exists>z. x + z = y)'],
    ['s\\<in>S \\<Longrightarrow> fundantivertex s \\<in> C0-s`\\<rightarrow>C0', 's\\<in>S \\<Longrightarrow> s`\\<rightarrow>C0 \\<in> fundadjset'],
    ['final(read a r) \\<longleftrightarrow> [a] \\<in> Lm r', '(R \\<Rightarrow> L) r'],
]
scores = model.predict(pairs)
print(scores)
# [-2.2402 -1.2744 -0.4268 -2.0137 -1.3398]

# Or rank different texts based on similarity to a single text
ranks = model.rank(
    'n \\<ge> 2 \\<Longrightarrow> n = fib i \\<Longrightarrow> n = fib j \\<Longrightarrow> i = j',
    [
        '2 \\<le> n \\<Longrightarrow> fib i \\<le> n \\<Longrightarrow> n < fib (Suc i) \\<Longrightarrow> 2 \\<le> i',
        'P256_on_curve P256_a P256_b P256_G',
        'x \\<le> y \\<longleftrightarrow> (\\<exists>z. x + z = y)',
        's\\<in>S \\<Longrightarrow> s`\\<rightarrow>C0 \\<in> fundadjset',
        '(R \\<Rightarrow> L) r',
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

## Evaluation

### Metrics

#### Cross Encoder Binary Classification

* Dataset: `afp_aug_val`
* Evaluated with [<code>CEBinaryClassificationEvaluator</code>](https://sbert.net/docs/package_reference/cross_encoder/evaluation.html#sentence_transformers.cross_encoder.evaluation.CEBinaryClassificationEvaluator)

| Metric                | Value      |
|:----------------------|:-----------|
| accuracy              | 0.8407     |
| accuracy_threshold    | -0.5009    |
| f1                    | 0.6215     |
| f1_threshold          | -1.1621    |
| precision             | 0.6736     |
| recall                | 0.5769     |
| **average_precision** | **0.7158** |

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

* Size: 78,285 training samples
* Columns: <code>sentence_0</code>, <code>sentence_1</code>, and <code>label</code>
* Approximate statistics based on the first 1000 samples:
  |         | sentence_0                                                                         | sentence_1                                                                         | label                                                          |
  |:--------|:-----------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------|:---------------------------------------------------------------|
  | type    | string                                                                             | string                                                                             | float                                                          |
  | details | <ul><li>min: 6 tokens</li><li>mean: 33.83 tokens</li><li>max: 196 tokens</li></ul> | <ul><li>min: 6 tokens</li><li>mean: 37.45 tokens</li><li>max: 197 tokens</li></ul> | <ul><li>min: 0.0</li><li>mean: 0.25</li><li>max: 1.0</li></ul> |
* Samples:
  | sentence_0                                                                                             | sentence_1                                                                                                           | label            |
  |:-------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------|:-----------------|
  | <code>n \<ge> 2 \<Longrightarrow> n = fib i \<Longrightarrow> n = fib j \<Longrightarrow> i = j</code> | <code>2 \<le> n \<Longrightarrow> fib i \<le> n \<Longrightarrow> n < fib (Suc i) \<Longrightarrow> 2 \<le> i</code> | <code>0.0</code> |
  | <code>P256_ECdomainParametersValid P256_a P256_b P256_G P256_n P256_h P256_t</code>                    | <code>P256_on_curve P256_a P256_b P256_G</code>                                                                      | <code>0.0</code> |
  | <code>x \<le> y \<Longrightarrow> d x \<le> d y</code>                                                 | <code>x \<le> y \<longleftrightarrow> (\<exists>z. x + z = y)</code>                                                 | <code>1.0</code> |
* Loss: [<code>BinaryCrossEntropyLoss</code>](https://sbert.net/docs/package_reference/cross_encoder/losses.html#binarycrossentropyloss) with these parameters:
  ```json
  {
      "activation_fn": "torch.nn.modules.linear.Identity",
      "pos_weight": null
  }
  ```

### Training Hyperparameters
#### Non-Default Hyperparameters

- `per_device_train_batch_size`: 32
- `per_device_eval_batch_size`: 32
- `num_train_epochs`: 2
- `fp16`: True

#### All Hyperparameters
<details><summary>Click to expand</summary>

- `do_predict`: False
- `prediction_loss_only`: True
- `per_device_train_batch_size`: 32
- `per_device_eval_batch_size`: 32
- `gradient_accumulation_steps`: 1
- `eval_accumulation_steps`: None
- `torch_empty_cache_steps`: None
- `learning_rate`: 5e-05
- `weight_decay`: 0.0
- `adam_beta1`: 0.9
- `adam_beta2`: 0.999
- `adam_epsilon`: 1e-08
- `max_grad_norm`: 1
- `num_train_epochs`: 2
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
- `fp16`: True
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
| Epoch  | Step | Training Loss | afp_aug_val_average_precision |
|:------:|:----:|:-------------:|:-----------------------------:|
| 0.2043 | 500  | 1.6745        | -                             |
| 0.4087 | 1000 | 0.4393        | -                             |
| 0.6130 | 1500 | 0.4336        | -                             |
| 0.8173 | 2000 | 0.4186        | 0.6981                        |
| 1.0    | 2447 | -             | 0.6960                        |
| 1.0217 | 2500 | 0.4174        | -                             |
| 1.2260 | 3000 | 0.4136        | -                             |
| 1.4303 | 3500 | 0.4111        | -                             |
| 1.6347 | 4000 | 0.4055        | 0.7158                        |


### Training Time
- **Training**: 2.7 minutes
- **Evaluation**: 5.9 seconds
- **Total**: 2.8 minutes

### Framework Versions
- Python: 3.12.13
- Sentence Transformers: 5.4.1
- Transformers: 5.0.0
- PyTorch: 2.10.0+cu128
- Accelerate: 1.13.0
- Datasets: 4.0.0
- Tokenizers: 0.22.2

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