# Project Objective

**Goal:** Fine-tune the Meta Llama 2 (7B) foundation model on a medical domain dataset. The resulting model should be capable of:

- Understanding and using domain-specific vocabulary, concepts, and relationships common in medical literature.
- Generating contextually relevant, accurate, and helpful medical text responses.

# Dataset Selection

**Requirements for the Dataset:**
- **Medical domain relevance**
- **Unstructured text**
- **Copyright-free / Open-license**

**Recommended Dataset:**
- **PubMed Central (PMC) Open Access Subset**
  - Large collection of biomedical and life sciences journal articles under open licenses.
  - Broad coverage of medical specializations.
  - Suitable for text mining and model fine-tuning.

**Alternatives:**
- **Project Gutenberg’s public domain medical texts** (historical, possibly outdated)
- **MIMIC-III or MIMIC-IV clinical notes** (more restrictive licenses, not fully copyright-free)

**Conclusion:**
Use the PMC Open Access Subset for its scale, diversity, and open-access licensing.

# Project Tasks

1. **Data Acquisition and Preprocessing**
   - Download PMC Open Access articles.
   - Filter by license to ensure open access.
   - Extract plain text, clean and preprocess (remove metadata, duplicates).

2. **Data Preparation for Fine-Tuning**
   - Tokenize using Llama 2 tokenizer.
   - Split into train, validation, and test sets.
   - Prepare data loaders for use in SageMaker and Hugging Face Transformers.

3. **Model Selection and Environment Setup**
   - Use Meta Llama 2 (7B) foundation model.
   - AWS SageMaker environment with GPU instances.
   - Leverage Hugging Face Transformers, Accelerate, and AWS Deep Learning Containers.

4. **Fine-Tuning the Model**
   - Hyperparameter tuning (learning rate, batch size, sequence length).
   - Use mixed precision training (FP16/BF16).
   - Monitor training using Amazon CloudWatch and SageMaker Experiments.

5. **Evaluation and Validation**
   - Intrinsic metrics: perplexity, validation loss.
   - Extrinsic evaluation: domain-specific prompts and expert qualitative feedback.
   - Compare results to baseline Llama 2 performance.

6. **Model Packaging and Deployment**
   - Save final model weights, tokenizer, and config in Amazon S3.
   - Deploy to a SageMaker endpoint for real-time inference.

7. **Documentation and Reporting**
   - **Report:**
     - Document process, dataset handling, training configurations.
     - Present results with metrics and example outputs.
   - **Presentation:**
     - Slides summarizing objectives, methodology, results, and lessons learned.

# Deliverables

1. **Trained Model**
   - Fine-tuned Llama 2 (7B) model with medical domain expertise.

2. **Report**
   - Detailed process documentation, challenges, and solutions.
   - Quantitative metrics and qualitative examples.

3. **Presentation**
   - Slide deck highlighting the project approach, outcomes, and future recommendations.

---

By following this plan, you will develop a medical-domain specialized Llama 2 (7B) model trained on open-access medical literature and provide thorough documentation and presentation materials.

