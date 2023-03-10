# Emotion_classification_performance_test
For comparing Emotion classification performance of different models on DailyDialog Dataset

[PRG-MoE](https://github.com/jdjin3000/PRG-MoE) referenced

## Dependencies
python 3.10.9<br>
pytorch 1.13.1<br>
pytorch-cuda 11.6<br>
tqdm 4.64.1<br>
numpy 1.23.5<br>
huggingface_hub 0.12.0<br>
cuda 11.6.1<br>
transformers 4.26.1<br>
scikit-learn 1.2.0<br>

## Dataset
The dataset used is [RECCON dataset](https://github.com/declare-lab/RECCON).

## Usage
To fine-tune (or test) pre-trained model, run this command:
```
python main.py
```

### Commit Conventions (from https://treasurebear.tistory.com/70)
π¨	`:art:`	μ½λμ κ΅¬μ‘°/νν κ°μ 	Improve structure / format of the code.<br>
β‘οΈ	`:zap:`	μ±λ₯ κ°μ 	Improve performance.<br>
π₯	`:fire:`	μ½λ/νμΌ μ­μ 	Remove code or files.<br>
π	`:bug:`	λ²κ·Έ μμ 	Fix a bug.<br>
π	`:ambulance:`	κΈ΄κΈ μμ 	Critical hotfix.<br>
β¨	`:sparkles:`	μ κΈ°λ₯	Introduce new features.<br>
π	`:memo:`	λ¬Έμ μΆκ°/μμ 	Add or update documentation.<br>
π	`:lipstick:`	UI/μ€νμΌ νμΌ μΆκ°/μμ 	Add or update the UI and style files.<br>
π	`:tada:`	νλ‘μ νΈ μμ	Begin a project.<br>
β	`:white_check_mark:`	νμ€νΈ μΆκ°/μμ 	Add or update tests.<br>
π	`:lock:`	λ³΄μ μ΄μ μμ 	Fix security issues.<br>
π	`:bookmark:`	λ¦΄λ¦¬μ¦/λ²μ  νκ·Έ	Release / Version tags.<br>
π	`:green_heart:`	CI λΉλ μμ 	Fix CI Build.<br>
π	`:pushpin:`	νΉμ  λ²μ  μμ‘΄μ± κ³ μ 	Pin dependencies to specific versions.<br>
π·	`:construction_worker:`	CI λΉλ μμ€ν μΆκ°/μμ 	Add or update CI build system.<br>
π	`:chart_with_upwards_trend:`	λΆμ, μΆμ  μ½λ μΆκ°/μμ 	Add or update analytics or track code.<br>
β»οΈ	`:recycle:`	μ½λ λ¦¬ν©ν λ§	Refactor code.<br>
β	`:heavy_plus_sign:`	μμ‘΄μ± μΆκ°	Add a dependency.<br>
β	`:heavy_minus_sign:`	μμ‘΄μ± μ κ±°	Remove a dependency.<br>
π§	`:wrench:`	κ΅¬μ± νμΌ μΆκ°/μ­μ 	Add or update configuration files.<br>
π¨	`:hammer:`	κ°λ° μ€ν¬λ¦½νΈ μΆκ°/μμ 	Add or update development scripts.<br>
π	`:globe_with_meridians:`	κ΅­μ ν/νμ§ν	Internationalization and localization.<br>
π©	`:poop:`	λ₯μΌ μ½λ	Write bad code that needs to be improved.<br>
βͺ	`:rewind:`	λ³κ²½ λ΄μ© λλλ¦¬κΈ°	Revert changes.<br>
π	`:twisted_rightwards_arrows:`	λΈλμΉ ν©λ³	Merge branches.<br>
π¦	`:package:`	μ»΄νμΌλ νμΌ μΆκ°/μμ 	Add or update compiled files or packages.<br>
π½	`:alien:`	μΈλΆ API λ³νλ‘ μΈν μμ 	Update code due to external API changes.<br>
π	`:truck:`	λ¦¬μμ€ μ΄λ, μ΄λ¦ λ³κ²½	Move or rename resources (e.g.: files paths routes).<br>
π	`:page_facing_up:`	λΌμ΄μΌμ€ μΆκ°/μμ 	Add or update license.<br>
π‘	`:bulb:`	μ£Όμ μΆκ°/μμ 	Add or update comments in source code.<br>
π»	`:beers:`	μ  μ·¨ν΄μ μ΄ μ½λ	Write code drunkenly.<br>
π	`:card_file_box:`	λ°μ΄λ²λ² μ΄μ€ κ΄λ ¨ μμ 	Perform database related changes.<br>
π	`:loud_sound:`	λ‘κ·Έ μΆκ°/μμ 	Add or update logs.<br>
π	`:see_no_evil:`	.gitignore μΆκ°/μμ 	Add or update a .gitignore file.<br>