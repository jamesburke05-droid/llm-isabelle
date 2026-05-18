---
tags:
- sentence-transformers
- sentence-similarity
- feature-extraction
- generated_from_trainer
- dataset_size:42069
- loss:MultipleNegativesRankingLoss
widget:
- source_sentence: "1. (\\<And>b B3.\n        \\<lbrakk>B2 = b # B3;\n         a \\\
    <cdot>\\<^sub>l\\<^sub>s\\<^sub>s\\<^sub>t\\<^sub>p \\<delta> = b;\n         A\
    \ \\<cdot>\\<^sub>l\\<^sub>s\\<^sub>s\\<^sub>t \\<delta> = B3\\<rbrakk>\n    \
    \    \\<Longrightarrow> thesis) \\<Longrightarrow>\n    thesis"
  sentences:
  - 'subst_lsst_cons: fixes a :: "''d strand_label \<times> (''e, ''f) stateful_strand_step"   and
    A :: "(''d strand_label \<times> (''e, ''f) stateful_strand_step) list"   and
    \<delta> :: "''f \<Rightarrow> (''e, ''f) Term.term" shows "a # A \<cdot>\<^sub>l\<^sub>s\<^sub>s\<^sub>t
    \<delta> = (a \<cdot>\<^sub>l\<^sub>s\<^sub>s\<^sub>t\<^sub>p \<delta>) # (A \<cdot>\<^sub>l\<^sub>s\<^sub>s\<^sub>t
    \<delta>)"'
  - 'fun_upd_eqD: fixes f :: "''a \<Rightarrow> ''b"   and x :: "''a"   and y :: "''b"   and
    g :: "''a \<Rightarrow> ''b"   and z :: "''b" assumes "f(x := y) = g(x := z)"
    shows "y = z"'
  - 'prv_prv_imp_trans: fixes var :: "''a set"   and trm :: "''b set"   and fmla ::
    "''c set"   and Var :: "''a \<Rightarrow> ''b"   and FvarsT :: "''b \<Rightarrow>
    ''a set"   and substT :: "''b \<Rightarrow> ''b \<Rightarrow> ''a \<Rightarrow>
    ''b"   and Fvars :: "''c \<Rightarrow> ''a set"   and subst :: "''c \<Rightarrow>
    ''b \<Rightarrow> ''a \<Rightarrow> ''c"   and num :: "''b set"   and eql :: "''b
    \<Rightarrow> ''b \<Rightarrow> ''c"   and cnj :: "''c \<Rightarrow> ''c \<Rightarrow>
    ''c"   and imp :: "''c \<Rightarrow> ''c \<Rightarrow> ''c"   and all :: "''a
    \<Rightarrow> ''c \<Rightarrow> ''c"   and exi :: "''a \<Rightarrow> ''c \<Rightarrow>
    ''c"   and prv :: "''c \<Rightarrow> bool"   and \<phi> :: "''c"   and \<chi>
    :: "''c"   and \<psi> :: "''c" assumes "Deduct var trm fmla Var FvarsT substT
    Fvars subst num eql cnj imp all exi prv"   and "\<phi> \<in> fmla"   and "\<chi>
    \<in> fmla"   and "\<psi> \<in> fmla"   and "prv (imp \<phi> \<chi>)"   and "prv
    (imp \<chi> \<psi>)" shows "prv (imp \<phi> \<psi>)"'
- source_sentence: "1. \\<lbrakk>x \\<sharp> y; x \\<sharp> c; x \\<sharp> P; a \\\
    <sharp> y;\n     a \\<sharp> c; a \\<sharp> P; a \\<sharp> N; x \\<sharp> M;\n\
    \     M \\<longrightarrow>\\<^sub>a Ax y a; M \\<noteq> Ax y a; M' = Ax y a;\n\
    \     \\<And>bb.\n        M{y:=<c>.bb} \\<longrightarrow>\\<^sub>a* (if y = y\n\
    \           then Cut <c>.bb y.Ax y a else Ax y a)\\<rbrakk>\n    \\<Longrightarrow>\
    \ Cut <a>.M{y:=<c>.P} x.N{y:=<c>.P} \\<longrightarrow>\\<^sub>a* Cut <c>.P x.N{y:=<c>.P}\n\
    \ 2. \\<lbrakk>x \\<sharp> y; x \\<sharp> c; x \\<sharp> P; a \\<sharp> y;\n \
    \    a \\<sharp> c; a \\<sharp> P; a \\<sharp> N; x \\<sharp> M;\n     M \\<longrightarrow>\\\
    <^sub>a M';\n     \\<And>b ba bb. M{b:=<ba>.bb} \\<longrightarrow>\\<^sub>a* M'{b:=<ba>.bb};\n\
    \     M \\<noteq> Ax y a\\<rbrakk>\n    \\<Longrightarrow> M' \\<noteq> Ax y a\
    \ \\<longrightarrow>\n                      Cut <a>.M{y:=<c>.P} x.N{y:=<c>.P}\
    \ \\<longrightarrow>\\<^sub>a* Cut <a>.M'{y:=<c>.P} x.N{y:=<c>.P}"
  sentences:
  - 'trans: fixes b :: "''b"   and a :: "''b"   and c :: "''b" assumes "b \<le> a"   and
    "c \<le> b" shows "c \<le> a"'
  - '2: shows "distinct (m # ms)"'
  - '"apply": fixes x :: "''a perm" shows "(\<langle>$\<rangle>) x \<in> {f. bij f
    \<and> finite {a. f a \<noteq> a}}"'
- source_sentence: 1. (c, s) \<Rightarrow> p \<Down> t \<Longrightarrow> 0 < p
  sentences:
  - 'modRule2Characterise: fixes Ps :: "''a list"   and C :: "(''b, ''c) sequent"
    assumes "(Ps, C) \<in> modRules2" shows "Ps \<noteq> [] \<and> (\<exists>F Fs.
    C = ( \<Empt> \<Rightarrow>* \<LM> Modal F Fs  \<RM>) \<or> C = ( \<LM> Modal
    F Fs  \<RM> \<Rightarrow>* \<Empt>))"'
  - '5: shows "\<not> member DenyAll aa"'
  - 'induct: fixes P :: "symbol list \<Rightarrow> (nat \<times> symbol \<times> symbol
    list) list \<Rightarrow> symbol list \<Rightarrow> bool"   and a0 :: "symbol list"   and
    a1 :: "(nat \<times> symbol \<times> symbol list) list"   and a2 :: "symbol list"
    assumes "\<And>a b. P a [] b"   and "\<And>a d D b. (\<And>x. P x D b) \<Longrightarrow>
    P a (d # D) b" shows "P a0 a1 a2"'
- source_sentence: 1. AE x in M. incseq (\<lambda>n. f x * indicat_real {..real n}
    x)
  sentences:
  - 'mult_eq_0_iff: fixes a :: "''b"   and b :: "''b" shows "(a * b = (0::''b)) =
    (a = (0::''b) \<or> b = (0::''b))"'
  - 'assoc: fixes a :: "''a"   and b :: "''a"   and c :: "''a" shows "a * b * c =
    a * (b * c)"'
  - 'same_length_different: fixes xs :: "''a list"   and ys :: "''a list" assumes
    "xs \<noteq> ys"   and "length xs = length ys" shows "\<exists>pre x xs'' y ys''.
    x \<noteq> y \<and> xs = pre @ [x] @ xs'' \<and> ys = pre @ [y] @ ys''"'
- source_sentence: "1. \\<lbrakk>type_wf h; document_ptr |\\<in>| document_ptr_kinds\
    \ h\\<rbrakk>\n    \\<Longrightarrow> h \\<turnstile> ok get_disconnected_nodes\
    \ document_ptr"
  sentences:
  - 'simp: fixes r :: "Vertex \<Rightarrow> Vertex" assumes "r \<in> simple_rotations"
    shows "r \<in> complex_rotations"'
  - '1: shows "inf_homomorphism ba_iso"'
  - 'get_disconnected_nodes_impl: shows "get_disconnected_nodes = a_get_disconnected_nodes"'
pipeline_tag: sentence-similarity
library_name: sentence-transformers
---

# SentenceTransformer

This is a [sentence-transformers](https://www.SBERT.net) model trained. It maps sentences & paragraphs to a 384-dimensional dense vector space and can be used for retrieval.

## Model Details

### Model Description
- **Model Type:** Sentence Transformer
<!-- - **Base model:** [Unknown](https://huggingface.co/unknown) -->
- **Maximum Sequence Length:** 256 tokens
- **Output Dimensionality:** 384 dimensions
- **Similarity Function:** Cosine Similarity
- **Supported Modality:** Text
<!-- - **Training Dataset:** Unknown -->
<!-- - **Language:** Unknown -->
<!-- - **License:** Unknown -->

### Model Sources

- **Documentation:** [Sentence Transformers Documentation](https://sbert.net)
- **Repository:** [Sentence Transformers on GitHub](https://github.com/huggingface/sentence-transformers)
- **Hugging Face:** [Sentence Transformers on Hugging Face](https://huggingface.co/models?library=sentence-transformers)

### Full Model Architecture

```
SentenceTransformer(
  (0): Transformer({'transformer_task': 'feature-extraction', 'modality_config': {'text': {'method': 'forward', 'method_output_name': 'last_hidden_state'}}, 'module_output_name': 'token_embeddings', 'architecture': 'BertModel'})
  (1): Pooling({'embedding_dimension': 384, 'pooling_mode': 'mean', 'include_prompt': True})
  (2): Normalize({})
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
from sentence_transformers import SentenceTransformer

# Download from the 🤗 Hub
model = SentenceTransformer("sentence_transformers_model_id")
# Run inference
sentences = [
    '1. \\<lbrakk>type_wf h; document_ptr |\\<in>| document_ptr_kinds h\\<rbrakk>\n    \\<Longrightarrow> h \\<turnstile> ok get_disconnected_nodes document_ptr',
    'get_disconnected_nodes_impl: shows "get_disconnected_nodes = a_get_disconnected_nodes"',
    'simp: fixes r :: "Vertex \\<Rightarrow> Vertex" assumes "r \\<in> simple_rotations" shows "r \\<in> complex_rotations"',
]
embeddings = model.encode(sentences)
print(embeddings.shape)
# [3, 384]

# Get the similarity scores for the embeddings
similarities = model.similarity(embeddings, embeddings)
print(similarities)
# tensor([[1.0000, 0.5418, 0.2557],
#         [0.5418, 1.0000, 0.4642],
#         [0.2557, 0.4642, 1.0000]])
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

* Size: 42,069 training samples
* Columns: <code>sentence_0</code> and <code>sentence_1</code>
* Approximate statistics based on the first 100 samples:
  |          | sentence_0                                                                          | sentence_1                                                                          |
  |:---------|:------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------|
  | type     | string                                                                              | string                                                                              |
  | modality | text                                                                                | text                                                                                |
  | details  | <ul><li>min: 12 tokens</li><li>mean: 61.38 tokens</li><li>max: 256 tokens</li></ul> | <ul><li>min: 12 tokens</li><li>mean: 56.58 tokens</li><li>max: 256 tokens</li></ul> |
* Samples:
  | sentence_0                                                                                                                                | sentence_1                                                                                                                                    |
  |:------------------------------------------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------|
  | <code>lemma subst_freshen_conclusions[simp]:<br>    assumes "pf \<in> set conclusions"<br>    shows "subst s (freshen a pf) = pf "</code> | <code>add: fixes f :: "'a \<Rightarrow> 'b"   and x :: "'a"   and y :: "'a" assumes "Modules.additive f" shows "f (x + y) = f x + f y"</code> |
  | <code>1. sigma_algebra (space P) (sets P)</code>                                                                                          | <code>semiring_of_sets_axioms: fixes M :: "'c measure" shows "semiring_of_sets (space M) (sets M)"</code>                                     |
  | <code>1. 0 < n (LEAST f. i' < f \<and> 0 < n f)</code>                                                                                    | <code>OF: shows "local.ofilter A"</code>                                                                                                      |
* Loss: [<code>MultipleNegativesRankingLoss</code>](https://sbert.net/docs/package_reference/sentence_transformer/losses.html#multiplenegativesrankingloss) with these parameters:
  ```json
  {
      "scale": 20.0,
      "similarity_fct": "cos_sim",
      "gather_across_devices": false,
      "directions": [
          "query_to_doc"
      ],
      "partition_mode": "joint",
      "hardness_mode": null,
      "hardness_strength": 0.0
  }
  ```

### Training Hyperparameters
#### Non-Default Hyperparameters

- `per_device_train_batch_size`: 32
- `per_device_eval_batch_size`: 32
- `num_train_epochs`: 1
- `multi_dataset_batch_sampler`: round_robin

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
- `multi_dataset_batch_sampler`: round_robin
- `router_mapping`: {}
- `learning_rate_mapping`: {}

</details>

### Training Logs
| Epoch  | Step | Training Loss |
|:------:|:----:|:-------------:|
| 0.3802 | 500  | 2.0752        |
| 0.7605 | 1000 | 2.0763        |


### Training Time
- **Training**: 9.3 minutes

### Framework Versions
- Python: 3.12.13
- Sentence Transformers: 5.5.0
- Transformers: 5.0.0
- PyTorch: 2.10.0+cu128
- Accelerate: 1.13.0
- Datasets: 4.8.5
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

#### MultipleNegativesRankingLoss
```bibtex
@misc{oord2019representationlearningcontrastivepredictive,
      title={Representation Learning with Contrastive Predictive Coding},
      author={Aaron van den Oord and Yazhe Li and Oriol Vinyals},
      year={2019},
      eprint={1807.03748},
      archivePrefix={arXiv},
      primaryClass={cs.LG},
      url={https://arxiv.org/abs/1807.03748},
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