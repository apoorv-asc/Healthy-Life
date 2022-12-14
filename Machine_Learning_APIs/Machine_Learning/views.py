from django.http import HttpResponse
from django.shortcuts import render
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

import numpy as np
import pandas as pd
from nltk.tag import pos_tag
import nltk
import joblib

from nltk.tag import pos_tag
from sklearn_crfsuite import CRF, metrics
from sklearn.metrics import make_scorer,confusion_matrix
from pprint import pprint
from sklearn.metrics import f1_score,classification_report
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split as tts
import string
import pycrfsuite

regressor = joblib.load("regressor_cost_prediction.sav")
RFClassifier_disease_predict = joblib.load("RFClassifier_disease_predict.pkl")
RFClassifier = joblib.load("RFClassifier.pkl")
# tagger = joblib.load("crf.model")

tagger = pycrfsuite.Tagger()
tagger.open('crf.model')

def home(request):
    return render(request,"home.html")

@csrf_exempt
def cost_pred(request):
    try:
        encounters = {'ambulatory': 0, 'emergency': 1, 'inpatient': 2, 'outpatient': 3, 'wellness': 4}
        hospitals = {'ADAMS PHYSICAL THERAPY  LLC': 0, 'ADCARE HOSPITAL OF WORCESTER INC': 1, 'ANNA JAQUES HOSPITAL': 2, 'AT CARE PLLC': 3, 'ATHOL MEMORIAL HOSPITAL': 4, 'BAYSTATE FRANKLIN MEDICAL CENTER': 5, 'BAYSTATE MEDICAL CENTER': 6, 'BAYSTATE WING HOSPITAL AND MEDICAL CENTERS': 7, 'BERKSHIRE MEDICAL CENTER INC - 1': 8, 'BETH ISRAEL DEACONESS HOSPITAL - NEEDHAM': 9, 'BETH ISRAEL DEACONESS HOSPITAL - PLYMOUTH': 10, 'BETH ISRAEL DEACONESS HOSPITAL-MILTON INC': 11, 'BETH ISRAEL DEACONESS MEDICAL CENTER': 12, 'BEVERLY HOSPITAL CORPORATION': 13, "BOSTON CHILDREN'S HOSPITAL": 14, 'BOSTON MEDICAL CENTER CORPORATION-': 15, "BRIGHAM AND WOMEN'S FAULKNER HOSPITAL": 16, "BRIGHAM AND WOMEN'S HOSPITAL": 17, 'BROCKTON AREA MULTI-SERVICES  INC.': 18, 'Boston Vet Center': 19, 'CAMBRIDGE HEALTH ALLIANCE': 20, 'CAMBRIDGE PUBLIC HEALTH COMMISSION': 21, 'CAPE COD HOSPITAL': 22, 'CAREWELL URGENT CARE CENTERS OF MA  PC': 23, 'CARNEY HOSPITAL': 24, 'CLINTON HOSPITAL ASSOCIATION': 25, 'COOLEY DICKINSON HOSPITAL INC THE': 26, 'COUNSELING ASSOCIATES OF DRACUT AND METHUEN': 27, 'DENTAL SURGEONS OF FALL RIVER PC': 28, 'EMERSON HOSPITAL -': 29, 'Edith Nourse Rogers Memorial Veterans Hospital (Bedford VA)': 30, 'FAIRVIEW HOSPITAL': 31, 'FALMOUTH HOSPITAL': 32, "FRANCISCAN CHILDREN'S HOSPITAL & REHAB CENTER": 33, 'Fitchburg Outpatient Clinic': 34, 'Framingham Outpatient Clinic': 35, 'GOOD SAMARITAN MEDICAL CENTER': 36, 'Gloucester Community Based Outpatient Clinic (CBOC)': 37, 'HALLMARK HEALTH MEDICAL ASSOCIATES INC': 38, 'HALLMARK HEALTH SYSTEM': 39, 'HAMPDEN PODIATRY ASSOCIATES': 40, 'HARRINGTON MEMORIAL HOSPITAL-1': 41, 'HEALTHALLIANCE HOSPITALS  INC': 42, 'HEBREW REHABILITATION CENTER': 43, 'HEYWOOD HOSPITAL -': 44, 'HOLY FAMILY HOSPITAL': 45, 'HOLYOKE MEDICAL CENTER': 46, 'Haverhill Community Based Outpatient Clinic (CBOC)': 47, 'Hyannis Outpatient Clinic': 48, 'LAHEY HOSPITAL & MEDICAL CENTER  BURLINGTON': 49, 'LAWRENCE GENERAL HOSPITAL': 50, 'LOWELL GENERAL HOSPITAL': 51, 'Lowell Outpatient Clinic': 52, 'MARLBOROUGH HOSPITAL': 53, "MARTHA'S VINEYARD HOSPITAL INC": 54, 'MASSACHUSETTS EYE AND EAR INFIRMARY -': 55, 'MASSACHUSETTS GENERAL HOSPITAL': 56, 'MERCY MEDICAL CTR': 57, 'MERRIMACK VALLEY PHYSICAL THERAPY': 58, 'METROWEST MEDICAL CENTER': 59, 'MILFORD REGIONAL MEDICAL CENTER': 60, 'MILTON CHIROPRACTIC AND REHABILITATION INC': 61, 'MORTON HOSPITAL': 62, 'MOUNT AUBURN HOSPITAL': 63, 'NANTUCKET COTTAGE HOSPITAL': 64, 'NASHOBA VALLEY MEDICAL CENTER': 65, 'NEW ENGLAND BAPTIST HOSPITAL': 66, 'NEW ENGLAND ORAL SURGERY ASSOCIATES LLC': 67, 'NEWTON-WELLESLEY HOSPITAL': 68, 'NOBLE HOSPITAL': 69, 'NORTH SHORE MEDICAL CENTER -': 70, 'NORWOOD HOSPITAL': 71, 'New Bedford Outpatient Clinic': 72, 'New Bedford Vet Center': 73, 'ORTHOPEDIC AND SPORTS PHYSICAL THERAPY  LLP': 74, 'PCP10127': 75, 'PCP118611': 76, 'PCP128586': 77, 'PCP136067': 78, 'PCP13802': 79, 'PCP139219': 80, 'PCP166697': 81, 'PCP191696': 82, 'PCP205980': 83, 'PCP26077': 84, 'PCP26110': 85, 'PCP3184': 86, 'PCP44465': 87, 'PCP4453': 88, 'PCP52699': 89, 'PCP67787': 90, 'PCP77608': 91, 'PCP89345': 92, 'PCP9047': 93, 'Plymouth Outreach Clinic': 94, 'Quincy Outpatient Clinic': 95, 'REHAB RESOLUTIONS INC': 96, 'RIVERSIDE RADIOLOGY MEDICAL GROUP INC': 97, "SAINT ANNE'S HOSPITAL": 98, "SHRINERS' HOSPITAL FOR CHILDREN (THE)": 99, "SHRINERS' HOSPITAL FOR CHILDREN - BOSTON  THE": 100, 'SIGNATURE HEALTHCARE BROCKTON HOSPITAL': 101, 'SOUTH BAY MENTAL HEALTH CENTER  INC.': 102, 'SOUTH SHORE HOSPITAL': 103, 'SOUTH SHORE RADIOLOGICAL ASSOCIATES  INC.': 104, 'SOUTHCOAST HOSPITAL GROUP  INC': 105, "ST ELIZABETH'S MEDICAL CENTER": 106, 'ST VINCENT HOSPITAL': 107, 'STURDY MEMORIAL HOSPITAL': 108, 'Springfield Vet Center': 109, 'TUFTS MEDICAL CENTER': 110, 'UHS OF WESTWOOD PEMBROKE INC': 111, 'UMASS MEMORIAL MEDICAL CENTER INC': 112, 'VA Boston Healthcare System  Brockton Campus': 113, 'VA Boston Healthcare System  Jamaica Plain Campus': 114, 'WINCHESTER HOSPITAL': 115, 'Worcester Outpatient Clinic': 116, 'Worcester Vet Center': 117}
        description = {'Asthma self management': 0, 'Cancer care plan': 1, 'Chronic obstructive pulmonary disease clinical management plan': 2, 'Demential management': 3, 'Diabetes self management plan': 4, 'Fracture care': 5, 'Head injury rehabilitation': 6, 'Hyperlipidemia clinical management plan': 7, 'Lifestyle education regarding hypertension': 8, 'Physical therapy procedure': 9, 'Psychiatry care plan': 10, 'Respiratory therapy': 11, 'Routine antenatal care': 12, 'Urinary tract infection care': 13, 'Wound care': 14}
        reason = {'Acute bronchitis (disorder)': 0, "Alzheimer's disease (disorder)": 1, 'Bullet wound': 2, 'Childhood asthma': 3, 'Chronic obstructive bronchitis (disorder)': 4, 'Closed fracture of hip': 5, 'Concussion with no loss of consciousness': 6, 'Cystitis': 7, 'Diabetes': 8, 'Escherichia coli urinary tract infection': 9, 'Facial laceration': 10, "Familial Alzheimer's disease of early onset (disorder)": 11, 'Fracture of ankle': 12, 'Fracture of clavicle': 13, 'Fracture of forearm': 14, 'Fracture of rib': 15, 'Fracture subluxation of wrist': 16, 'Hyperlipidemia': 17, 'Hypertension': 18, 'Injury of anterior cruciate ligament': 19, 'Injury of medial collateral ligament of knee': 20, 'Laceration of foot': 21, 'Laceration of forearm': 22, 'Laceration of hand': 23, 'Laceration of thigh': 24, 'Major depression disorder': 25, 'Malignant tumor of colon': 26, 'Neoplasm of prostate': 27, 'Normal pregnancy': 28, 'Prediabetes': 29, 'Pulmonary emphysema (disorder)': 30, 'Rupture of patellar tendon': 31, 'Sprain of ankle': 32, 'Tear of meniscus of knee': 33}
        diagnosis = {'Admission to orthopedic department': 0, 'Admission to trauma surgery department': 1, 'Alpha-fetoprotein test': 2, 'Ankle X-ray': 3, 'Asthma screening': 4, 'Augmentation of labor': 5, 'Auscultation of the fetal heart': 6, 'Blood typing  RH typing': 7, 'Bone density scan (procedure)': 8, 'Bone immobilization': 9, 'Chest X-ray': 10, 'Childbirth': 11, 'Chlamydia antigen test': 12, 'Clavicle X-ray': 13, 'Combined chemotherapy and radiation therapy (procedure)': 14, 'Cytopathology procedure  preparation of smear  genital source': 15, 'Digital examination of rectum': 16, 'Electrical cardioversion': 17, 'Evaluation of uterine fundal height': 18, 'Extraction of wisdom tooth': 19, 'Fetal anatomy study': 20, 'Gonorrhea infection test': 21, 'Hearing examination (procedure)': 22, 'Hemoglobin / Hematocrit / Platelet count': 23, 'Hepatitis B Surface Antigen Measurement': 24, 'Hepatitis C antibody test': 25, 'High resolution computed tomography of chest without contrast (procedure)': 26, 'Human immunodeficiency virus antigen test': 27, 'Injection of tetanus antitoxin': 28, 'Intramuscular injection': 29, 'Knee X-ray': 30, 'Measurement of Varicella-zoster virus antibody': 31, 'Measurement of respiratory function (procedure)': 32, 'Medication Reconciliation (procedure)': 33, 'Pelvis X-ray': 34, 'Physical examination of mother': 35, 'Plain chest X-ray (procedure)': 36, 'Prostatectomy': 37, 'Pulmonary rehabilitation (regime/therapy)': 38, 'Rubella screening': 39, 'Skin test for tuberculosis': 40, 'Spirometry (procedure)': 41, 'Sputum examination (procedure)': 42, 'Standard pregnancy test': 43, 'Suture open wound': 44, 'Syphilis infection test': 45, 'Ultrasound scan for fetal viability': 46, 'Upper arm X-ray': 47, 'Urine culture': 48, 'Urine protein test': 49, 'Urine screening test for diabetes': 50, 'X-ray or wrist': 51, 'positive screening for PHQ-9': 52}
        lis = []
        data = json.loads(request.body.decode("utf-8"))
        lis.append(encounters[data['enc']])
        lis.append(hospitals[data['hosp']]/117)
        lis.append(description[data['desc']]/14)
        lis.append(reason[data['rsn']]/33)
        lis.append(diagnosis[data['diag']]/52)
        lis.append((int(data['days'])-7)/(840-7))
        
        res = regressor.predict([lis])
        return JsonResponse({"res":res[0]})
    except:
        return JsonResponse({"res":"Error"})

@csrf_exempt
def disease_pred(request):
    features = ["Abdomen, Acute","Abdominal Pain","Abdominal bloating","Abdominal colic","Abducens Nerve Diseases","Abnormal bowel sounds","Abnormal breathing","Abnormal heart beat","Abnormal sputum","Abortion, Habitual","Acidosis","Acidosis, Respiratory","Acquired kyphosis","Acrocyanosis","Acrodermatitis enteropathica","Action Tremor","Acute dyspnea","Acute rotatory vertigo","Adynamia","Affective ambivalence","Agitation","Agranulocytosis","Airway Obstruction","Akathisia","Albuminuria","Alkalosis, Respiratory","Alopecia","Alopecia effluvium","Alveolitis","Amaurosis","Amaurosis Fugax","Amblyopia","Amenorrhea","Amnesia","Amyloidosis","Anal Fissure","Anal abscess","Anemia","Anemia due to blood loss","Anemia, Hemolytic","Anemia, Megaloblastic","Angina Pectoris","Angor mortis","Anisocytosis","Annular Erythema","Anorexia","Anterior uveitis","Anti-transglutaminase antibody","Anuria","Anxiety","Aortic Aneurysm","Apathy","Aphasia","Aphthous Stomatitis","Arachnodactyly","Arthralgia","Arthritis","Arthritis, Reactive","Ascites","Asterixis","Ataxia","Atrial Fibrillation","Atrophic condition of skin","Atrophie blanche","Atrophy of testis","Aura","Auscultation","Autistic Disorder","Autoimmune hemolytic anemia","Automatism","Back Pain","Baresthesia","Bartholinitis","Basophilia","Beading of ribs","Bell Palsy","Benign Prostatic Hyperplasia","Bicytopenia","Bigeminal pulse","Biopsy of liver (procedure)","Blast Phase","Blindness","Blood in stool","Bone marrow hyperplasia","Bone pain","Botulism","Bradycardia","Bronchial Spasm","Bronchiectasis","Bronchitis","Bronchopneumonia","Bronchopulmonary infection","Brown urine","Bulbar palsy","Bulimia","Bulla","Burning sensation","Bursitis","Ca++ increased","Cachexia","Calcinosis cutis","Cancer cachexia","Candidiasis","Capsulorhexis","Carcinoma of Endocrine Gland","Cardiac Arrhythmia","Cardiac Tamponade","Cardiac asthma","Cardiomegaly","Casts urinary red cells positive","Catatonia","Cellular Vesicle","Cellulitis","Cerebellar Ataxia","Cerebral Edema","Cerebral hypoperfusion","Cerebrovascular accident","Cheilitis","Chest Pain","Chills","Cholecystolithiasis","Cholelithiasis","Cholestasis","Chronic cough","Chronic diarrhea","Chronic fatigue","Chronic passive congestion of liver","Chronic skin ulcer","Chronic urticaria","Cirrhosis","Clubbed Fingers","Clubbing","Colorectal Carcinoma","Comatose","Common Cold","Conduction disorder of the heart","Conductive hearing loss","Confusion","Congenital clinodactyly","Congenital flat foot","Congenital hypothyroidism without goiter","Congenital macroglossia","Congenital pectus carinatum","Congenital pectus excavatum","Conjunctivitis","Constipation","Contact Dermatitis","Continuous leakage of urine","Cor pulmonale","Cornea verticillata","Corneal Ulcer","Coronary artery embolism","Coughing","Craniotabes","Creatine kinase measurement","Creatinine increased","Cushingoid facies","Cyanosis","Cystitis","Cytopenia","Dactylitis","Decrease in appetite","Deglutition Disorders","Dehydration","Delusion of observation","Delusion of reference","Delusions","Dental caries","Depersonalization","Derealization","Dermatitis Herpetiformis","Dermatitis, Atopic","Dermatomyositis","Developmental delay (disorder)","Diarrhea","Digestive System Fistula","Dilatation of aorta","Dilation of esophagus due to disease","Diplopia","Disease of capillaries","Disorder of eye","Disorder of skeletal system","Disorientation","Disseminated Intravascular Coagulation","Distention","Disturbances in consciousness NEC","Diuretics","Dizziness","Dizzy spells","Drowsiness","Dry cough","Dry skin","Dupuytren Contracture","Dysarthria","Dysdiadochokinesis","Dyskinetic syndrome","Dysmenorrhea","Dyspepsia","Dysphonia","Dyspnea","Dyspnea on exertion","Dysthymic Disorder","Dystrophia unguium","Dysuria","Ear Inflammation","Ear discharge","Earache","Ecchymosis","Echolalia","Eczema","Edema","Elevated total bilirubin","Emaciation","Embolism","Emphysematous gangrene","Encephalopathies","Endocarditis","Endomyocardial Fibrosis","Enophthalmos","Enteropathic arthritis","Enthesopathy","Eosinophilia","Epilepsy","Episcleritis","Epistaxis","Erectile dysfunction","Ergotherapy","Eructation","Erythema","Erythema Nodosum","Erythrocytosis","Erythromelalgia","Esophageal Dysphagia","Esophagitis","Euphoric mood","Exanthema","Exanthema Subitum","Exertional headache","Exfoliative dermatitis","Exophthalmos","Eye pain","Facial edema","Fatigue","Fatty Liver","Faucial diphtheria","Feeling of lump in throat","Ferritin high","Fetal Growth Retardation","Fetor hepaticus","Fever","Fibrosis","Fissure in skin","Flank Pain","Flatfoot","Flatulence","Flatulence, eructation, and gas pain","Fluid overload","Fluorine","Flushing","Folic Acid Deficiency","Food Poisoning","Foreign body sensation","Formication","Fracture","Gait abnormality","Gastric ulcer","Gastrin increased","Gastritis","Gastrointestinal Hemorrhage","Gingival Hemorrhage","Gingivitis","Glomerulonephritis","Glossalgia","Glycogenolysis","Glycosuria","Goiter","Grimaces","Gynecomastia","HIV cardiomyopathy","Halitosis","Hallucinations","Headache","Hearing problem","Heart Failure, Right-Sided","Heart failure","Heart murmur","Heartburn","Heberden\'s node","Hemarthrosis","Hematemesis","Hematoma","Hematuria","Hemiparesis","Hemiplegia","Hemolysis (disorder)","Hemoptysis","Hemorrhage","Hemorrhagic Disorders","Hemosiderosis","Hemospermia","Hepatic congestion","Hepatitis","Hepatitis, Chronic","Hepatomegaly","Hepatomegaly, not elsewhere classified","Hepatosplenomegaly","Herpes zoster dermatitis","Hiccup","Hilar lymphadenopathy","Hirsutism","Hoarseness","Hot flushes","Hydrocephalus","Hydrops of gallbladder","Hypercalcemia","Hypercapnia","Hypercholesterolemia","Hypercholesterolemia result","Hyperemia","Hyperhidrosis disorder","Hyperkalemia","Hyperkeratosis","Hyperlipidemia","Hyperlipoproteinemias","Hypermetabolism","Hypernatremia","Hyperpigmentation","Hyperreflexia","Hypersplenism","Hypertensive disease","Hypertrichosis","Hypertriglyceridemia","Hyperuricemia","Hyperventilation","Hypesthesia","Hypocalcemia","Hypochlorhydria","Hypogammaglobulinemia","Hypoglycemia","Hypogonadism","Hypokalemia","Hyponatremia","Hypotension","Hypothermia, natural","Hypotrichosis","Hypoventilation","Hypoxia","Hypoxic arrest","Icterus","Ileus","Immunoglobulin Light Chains","Impaired glucose tolerance","Incontinence","Increased frequency of micturition","Increased susceptibility to infections","Infertility","Intercostal neuralgia","Intermittent fever","Intestinal Pseudo-Obstruction","Iridocyclitis","Iritis","Iron deficiency anemia","Irritable Mood","Irritative cough","Ischemia","Jaundice, Obstructive","Kandinsky Syndrome","Kaposi Varicelliform Eruption","Keratitis","Kidney Failure","Kidney Failure, Acute","Kyphosis deformity of spine","Lack of libido","Lactate dehydrogenase measurement","Laryngeal Edema","Laryngeal Nerve Palsy, Recurrent","Laryngitis","Lead line","Left Bundle-Branch Block","Left-Sided Heart Failure","Leg edema","Lethargy","Leukocytosis","Leukopenia","Leukoplakia","Linear atrophy","Lipid Metabolism Disorders","Lipiduria","Lipodermatosclerosis","Livedo Reticularis","Livedo vasculitis","Liver Cirrhosis","Liver Dysfunction","Liver enzymes abnormal","Long narrow head","Low Cardiac Output Syndrome","Lung Abscess","Lupus Nephritis","Lymphadenopathy","Lymphocytosis","Lymphomas NEC","Lymphopenia","Lytic lesion","Macrocytosis","Macular rash","Malabsorption","Malabsorption Syndrome","Malaise","Mariscae","Mastoiditis","Mean venous pressure increased","Measles","Meconium ileus","Megacolon","Megaesophagus","Melena","Meningeal Leukemia","Meningism","Meningitis","Meningoencephalitis","Menorrhagia","Mental Depression","Metabolic alkalosis","Metrorrhagia","Microangiopathic hemolytic anemia","Microscopic hematuria","Microstomia","Migraine Disorders","Mimetic Muscles","Miosis disorder","Mitral Valve Insufficiency","Mitral Valve Prolapse Syndrome","Mitral facies","Monoclonal Gammapathies","Monoclonal Gammopathy of Undetermined Significance","Monocytopenia","Motor retardation","Mouth Breathing","Mucous membrane dryness","Mucous membrane eruption","Multiple telangiectases","Muscle Cramp","Muscle Spasticity","Muscle Weakness","Muscular Atrophy","Mutism","Myalgia","Myasthenias","Mycoses","Mydriasis","Myocardiac abscess","Myocardial Infarction","Myocardial fibrosis","Myocarditis","Myoglobinuria","Myopathy","Myopia","Myositis","Myxedema","Nasal obstruction present finding","Nasolabial sulcus","Nausea","Neck Pain","Neck stiffness","Necrotizing Enterocolitis","Nephritis","Nephrocalcinosis","Nephrolithiasis","Nephrotic Syndrome","Neutropenia","Night Blindness","Night sweats","Nocturia","Nocturnal cough","Normochromic anemia","Normocytic anemia","Nystagmus","Obesity, Abdominal","Obstruction","Oliguria","Ophthalmoplegia","Opisthotonus","Optic Atrophy","Optic Neuritis","Oral Ulcer","Orthopnea","Orthostatic dysregulation","Osteomyelitis","Osteoporosis","Other and unspecified skin changes","Other difficulties with micturition","Other fall on same level causing accidental injury","Other fecal abnormalities","Other hearing loss","Other peptic ulcers","Otitis Media","Otitis Media with Effusion","Pain","Pain neck/shoulder","Pain upon movement","Pallor","Palmar erythema","Palpitations","Pancarditis","Pancreatic Insufficiency","Pancytopenia","Papilledema","Paraesthesias and dysaesthesias","Paralysis and paresis (excl cranial nerve)","Paraphasia","Paraplegia","Paresis","Paresthesia","Parkinsonian Disorders","Parotitis","Paroxysmal atrial tachycardia","Pathological accumulation of air in tissues","Pathological fracture","Peptic Esophagitis","Perforation (observation)","Pericardial effusion","Pericarditis","Periodontitis","Peripheral Neuropathy","Peripheral cyanosis","Peritonitis","Peritonsillar Abscess","Personality change","Pertussis","Petechiae","Phakectomy","Pharyngitis","Phonophobia","Photophobia","Pityriasis alba","Plantar erythema","Pleural effusion disorder","Pleural fluid = exudate","Pleurisy","Pneumonia","Pneumonia, Interstitial","Pneumothorax","Poikilocytosis","Polyarthritis","Polychromatophilic stain reaction","Polydipsia","Polyglobulia","Polyhydramnios","Polymyositis","Polyneuritis","Polyneuropathy","Polyserositis","Polyuria","Portal vein thrombosis","Pregnancy","Premature Cardiac Complex","Premature ventricular contractions","Proctitis","Productive cough","Prolonged expiration","Prolonged menses","Proteinuria","Protrusio acetabuli","Pruritus","Pruritus Ani","Pseudofolliculitis","Pseudogout","Psoriasis","Psychiatric symptoms NEC","Psychotic Disorders","Ptosis","Pulmonary Edema","Pulmonary Emphysema","Pulmonary Fibrosis","Pulmonary Hypertension","Pulmonary aspiration","Pulmonary congestion","Pulmonary hemorrhage","Pulmonary microemboli","Pulse irregular","Pulsus paradoxus","Pupillary reflex test","Purpura","Pyoderma Gangrenosum","Raynaud Disease","Rectal Prolapse","Redness of eye","Regurgitation","Renal Colic","Renal Insufficiency","Renal infarction","Respiratory Insufficiency","Respiratory Tract Infections","Respiratory arrest","Restlessness","Reticulocytopenia","Reticulocytosis","Retinoids","Retrobulbar Neuritis","Retrognathia","Rhabdomyolysis","Rheology","Rhinitis","Rhonchi","Right bundle branch block","Right lower quadrant pain","Rotary Nystagmus","Sacroiliitis","Sclerodactyly","Scleroderma","Scoliosis, unspecified","Scotoma","Seborrheic dermatitis","Seborrheic dermatitis of scalp","Secondary hyperparathyroidism, not elsewhere classified","Seizures","Seizures, Focal","Sense Organs","Sepsis","Serositis","Shaking inside","Shock","Shock, Cardiogenic","Short-stepped gait","Sialorrhea","Sinus Tachycardia","Sinus bradycardia","Sinusitis","Skin hemorrhages","Skin sensation disturbance","Sleep Disorders","Sleeplessness","Slight temperature","Slow speech","Snoring","Sopor","Sore Throat","Sore to touch","Spasm glottis","Spastic gait","Speech Disorders","Speech and language abnormalities","Spider nevus","Splenomegaly","Splenomegaly, not elsewhere classified","Spontaneous abortion","Stahli\'s line","Stasis dermatitis","Status Asthmaticus","Steatorrhea","Stomach ache","Stomatitis","Strawberry tongue","Stridor","Structure of platysma muscle","Stupor","Subileus","Sudden Cardiac Death","Sweating","Swelling","Syncope","Syphilis","Tachycardia, Ventricular","Tachypnea","Temperature regulation disorder","Temporospatial disorientation","Tenosynovitis","Tetanus","Tetany","Thought broadcast","Thought insertion","Thought withdrawal","Thrombocytopenia","Thrombocytosis","Thrombophilia","Thrombophlebitis migrans","Thrombosis of renal vein","Tinea corporis (disorder)","Tinnitus","Tonsillitis","Tooth Extraction","Tracheobronchitis","Trachyonychia","Transient Ischemic Attack","Tremor","Tremulousness","Tricuspid Valve Insufficiency","Trigeminal Neuralgia","Ulcers NEC","Unconscious State","Unintentional weight loss","Urethritis","Urgency of micturition","Uric acid high","Urinary Bladder","Urinary Incontinence","Urinary Retention","Urticaria","Uterine Cervicitis","Uveitis","Uveitis, Posterior","Varicocele","Varicosity","Vascular constriction (function)","Vasculitis","Vasospasm","Ventricular Fibrillation","Ventricular arrhythmia","Vertigo","Vigilance decreased","Virilism","Visual disturbance","Vitamin B 12 Deficiency","Vitamin Deficiency","Vitamin K Deficiency","Vitreous floaters","Vomiting","Wasting Syndrome","Waxy flexibility","Weakness","Weight Gain","Wheezing","Wounds and Injuries","Courvoisier\'s gallbladder","Murphy\'s sign","Non Smoker","impaired cognition","abdominal tenderness","abnormal sensation","abnormally hard consistency","abortion","abscess bacterial","absences finding","achalasia","ache","adverse reaction","air fluid level","alcohol binge episode","alcoholic withdrawal symptoms","ambidexterity","anosmia","aphagia","apyrexial","asthenia","asymptomatic","atypia","awakening early","barking cough","bedridden","behavior hyperactive","behavior showing increased motor activity","blackout","blanch","bleeding of vagina","bowel sounds decreased","bradykinesia","breakthrough pain","breath sounds decreased","breath-holding spell","breech presentation","bruit","cardiovascular finding","catching breath","charleyhorse","chest discomfort","chest tightness","choke","cicatrisation","clammy skin","clonus","clumsiness","consciousness clear","coordination abnormal","cystic lesion","debilitation","decompensation","decreased body weight","decreased stool caliber","decreased translucency","difficulty","difficulty passing urine","disequilibrium","distended abdomen","distress respiratory","disturbed family","drool","dullness","dysesthesia","dyspareunia","egophony","elation","emphysematous change","energy increased","enuresis","estrogen use","excruciating pain","exhaustion","extrapyramidal sign","extreme exhaustion","facial paresis","fall","fatigability","fear of falling","fecaluria","feces in rectum","feeling hopeless","feeling strange","feeling suicidal","feels hot/feverish","flare","floppy","food intolerance","frail","fremitus","frothy sputum","furuncle","gag","gasping for breath","general discomfort","general unsteadiness","giddy mood","gravida 0","gravida 10","green sputum","groggy","guaiac positive","gurgle","hacking cough","hallucinations auditory","hallucinations visual","has religious belief","hearing impairment","heavy feeling","heavy legs","hematochezia","hematocrit decreased","heme positive","hemianopsia homonymous","hemodynamically stable","herzrasen","homelessness","homicidal thoughts","hunger","hydropneumothorax","hyperacusis","hyperemesis","hypersomnia","hypersomnolence","hypertonicity","hypoalbuminemia","hypokinesia","hypometabolism","hypoproteinemia","hypoxemia","immobile","impaired cognition.1","inappropriate affect","incoherent","intermenstrual heavy bleeding","intoxication","jugular venous distention","labored breathing","lameness","large-for-dates fetus","left\\xa0atrial\\xa0hypertrophy","left\xa0atrial\xa0hypertrophy","lesion","lightheadedness","lip smacking","loose associations","low back pain","lung nodule","macerated skin","macule","mass in breast","mass of body structure","mediastinal shift","mental status changes","metastatic lesion","milky","moan","monoclonal","monocytosis","mood depressed","moody","muscle hypotonia","muscle twitch","myoclonus","nasal discharge present","nasal flaring","nausea and vomiting","neologism","nervousness","nightmare","no known drug allergies","no status change","noisy respiration","nonsmoker","numbness","numbness of hand","orthostasis","out of breath","overweight","pain foot","pain in lower limb","painful swallowing","pansystolic murmur","para 1","para 2","paralyse","paraparesis","passed stones","patient non compliance","photopsia","pin-point pupils","pleuritic pain","pneumatouria","polymyalgia","poor dentition","poor feeding","posterior\xa0rhinorrhea","posturing","presence of q wave","pressure chest","previous pregnancies 2","primigravida","prodrome","projectile vomiting","prostate tender","prostatism","prostatitis","proteinemia","pseudomembranous colitis","pulse absent","pustule","qt interval prolonged","r wave feature","rale","rambling speech","rapid shallow breathing","red blotches","redness","regurgitates after swallowing","renal angle tenderness","rest pain","retch","retropulsion","rhd positive","rigor - temperature-associated observation","rolling of eyes","room spinning","satiety early","scar tissue","sciatica","scleral\\xa0icterus","scleral\xa0icterus","scratch marks","sedentary","sensory discomfort","shooting pain","shortness of breath","side pain","sinus rhythm","sleepy","slowing of urinary stream","sneeze","sniffle","snuffle","spasm","speech slurred","spontaneous rupture of membranes","sputum purulent","st segment depression","st segment elevation","stiffness","stinging sensation","stool color yellow","stuffy nose","suicidal","superimposition","swelling of hands (finding)","symptom aggravating factors","systolic ejection murmur","systolic murmur","t wave inverted","tenesmus","terrify","thicken","throbbing sensation quality","titubation","todd paralysis","tonic seizures","transaminitis","transsexual","tremor resting","tumor cell invasion","unable to concentrate","uncoordination","underweight","unhappy","unresponsiveness","unsteady gait","unwell","urge incontinence","urinary hesitation","urinoma","verbal auditory hallucinations","verbally abusive behavior","vision blurred","weepiness","welt","wheelchair bound","withdraw","worry","yellow sputum",]

    data = json.loads(request.body.decode("utf-8"))

    search = data["sym"]

    Fea_Dict = {}
    for i,f in enumerate(features):
        Fea_Dict[f] = i

    sample = np.zeros((len(features),), dtype=np.int)
    for i,s in enumerate(search):
        sample[Fea_Dict[s]] = 1
    sample_in = np.array(sample).reshape(1,len(sample))

    c  = pd.DataFrame(RFClassifier.predict_proba(sample_in), columns=RFClassifier.classes_)
    c = c.sort_values(axis=1, by= 0, ascending= False)
    first_n_column  = c.iloc[: , :10]
    d = first_n_column.to_dict('split')
    disease_arr = d['columns']
    prob_arr = []
    for i in d['data'][0]:
        prob_arr.append(i*100)

    return JsonResponse({"Diseases":disease_arr,"Probabilities":prob_arr})

@csrf_exempt
def ner(request):

    sigs = ["for 5 to 6 days", "inject 2 units", "x 2 weeks", "x 3 days", "every day", "every 2 weeks", "every 3 days", "every 1 to 2 months", "every 2 to 6 weeks", "every 4 to 6 days", "take two to four tabs", "take 2 to 4 tabs", "take 3 tabs orally bid for 10 days at bedtime", "swallow three capsules tid orally", "take 2 capsules po every 6 hours", "take 2 tabs po for 10 days", "take 100 caps by mouth tid for 10 weeks", "take 2 tabs after an hour", "2 tabs every 4-6 hours", "every 4 to 6 hours", "q46h", "q4-6h", "2 hours before breakfast", "before 30 mins at bedtime", "30 mins before bed", "and 100 tabs twice a month", "100 tabs twice a month", "100 tabs once a month", "100 tabs thrice a month", "3 tabs daily for 3 days then 1 tab per day at bed", "30 tabs 10 days tid", "take 30 tabs for 10 days three times a day", "qid q6h", "bid", "qid", "30 tabs before dinner and bedtime", "30 tabs before dinner & bedtime", "take 3 tabs at bedtime", "30 tabs thrice daily for 10 days ", "30 tabs for 10 days three times a day", "Take 2 tablets a day", "qid for 10 days", "every day", "take 2 caps at bedtime", "apply 3 drops before bedtime", "take three capsules daily", "swallow 3 pills once a day", "swallow three pills thrice a day", "apply daily", "apply three drops before bedtime", "every 6 hours", "before food", "after food", "for 20 days", "for twenty days", "with meals"]
    input_sigs = [['for', '5', 'to', '6', 'days'], ['inject', '2', 'units'], ['x', '2', 'weeks'], ['x', '3', 'days'], ['every', 'day'], ['every', '2', 'weeks'], ['every', '3', 'days'], ['every', '1', 'to', '2', 'months'], ['every', '2', 'to', '6', 'weeks'], ['every', '4', 'to', '6', 'days'], ['take', 'two', 'to', 'four', 'tabs'], ['take', '2', 'to', '4', 'tabs'], ['take', '3', 'tabs', 'orally', 'bid', 'for', '10', 'days', 'at', 'bedtime'], ['swallow', 'three', 'capsules', 'tid', 'orally'], ['take', '2', 'capsules', 'po', 'every', '6', 'hours'], ['take', '2', 'tabs', 'po', 'for', '10', 'days'], ['take', '100', 'caps', 'by', 'mouth', 'tid', 'for', '10', 'weeks'], ['take', '2', 'tabs', 'after', 'an', 'hour'], ['2', 'tabs', 'every', '4-6', 'hours'], ['every', '4', 'to', '6', 'hours'], ['q46h'], ['q4-6h'], ['2', 'hours', 'before', 'breakfast'], ['before', '30', 'mins', 'at', 'bedtime'], ['30', 'mins', 'before', 'bed'], ['and', '100', 'tabs', 'twice', 'a', 'month'], ['100', 'tabs', 'twice', 'a', 'month'], ['100', 'tabs', 'once', 'a', 'month'], ['100', 'tabs', 'thrice', 'a', 'month'], ['3', 'tabs', 'daily', 'for', '3', 'days', 'then', '1', 'tab', 'per', 'day', 'at', 'bed'], ['30', 'tabs', '10', 'days', 'tid'], ['take', '30', 'tabs', 'for', '10', 'days', 'three', 'times', 'a', 'day'], ['qid', 'q6h'], ['bid'], ['qid'], ['30', 'tabs', 'before', 'dinner', 'and', 'bedtime'], ['30', 'tabs', 'before', 'dinner', '&', 'bedtime'], ['take', '3', 'tabs', 'at', 'bedtime'], ['30', 'tabs', 'thrice', 'daily', 'for', '10', 'days'], ['30', 'tabs', 'for', '10', 'days', 'three', 'times', 'a', 'day'], ['take', '2', 'tablets', 'a', 'day'], ['qid', 'for', '10', 'days'], ['every', 'day'], ['take', '2', 'caps', 'at', 'bedtime'], ['apply', '3', 'drops', 'before', 'bedtime'], ['take', 'three', 'capsules', 'daily'], ['swallow', '3', 'pills', 'once', 'a', 'day'], ['swallow', 'three', 'pills', 'thrice', 'a', 'day'], ['apply', 'daily'], ['apply', 'three', 'drops', 'before', 'bedtime'], ['every', '6', 'hours'], ['before', 'food'], ['after', 'food'], ['for', '20', 'days'], ['for', 'twenty', 'days'], ['with', 'meals']]
    output_labels = [['FOR', 'Duration', 'TO', 'DurationMax', 'DurationUnit'], ['Method', 'Qty', 'Form'], ['FOR', 'Duration', 'DurationUnit'], ['FOR', 'Duration', 'DurationUnit'], ['EVERY', 'Period'], ['EVERY', 'Period', 'PeriodUnit'], ['EVERY', 'Period', 'PeriodUnit'], ['EVERY', 'Period', 'TO', 'PeriodMax', 'PeriodUnit'], ['EVERY', 'Period', 'TO', 'PeriodMax', 'PeriodUnit'], ['EVERY', 'Period', 'TO', 'PeriodMax', 'PeriodUnit'], ['Method', 'Qty', 'TO', 'Qty', 'Form'], ['Method', 'Qty', 'TO', 'Qty', 'Form'], ['Method', 'Qty', 'Form', 'PO', 'BID', 'FOR', 'Duration', 'DurationUnit', 'AT', 'WHEN'], ['Method', 'Qty', 'Form', 'TID', 'PO'], ['Method', 'Qty', 'Form', 'PO', 'EVERY', 'Period', 'PeriodUnit'], ['Method', 'Qty', 'Form', 'PO', 'FOR', 'Duration', 'DurationUnit'], ['Method', 'Qty', 'Form', 'BY', 'PO', 'TID', 'FOR', 'Duration', 'DurationUnit'], ['Method', 'Qty', 'Form', 'AFTER', 'Period', 'PeriodUnit'], ['Qty', 'Form', 'EVERY', 'Period', 'PeriodUnit'], ['EVERY', 'Period', 'TO', 'PeriodMax', 'PeriodUnit'], ['Q46H'], ['Q4-6H'], ['Qty', 'PeriodUnit', 'BEFORE', 'WHEN'], ['BEFORE', 'Qty', 'M', 'AT', 'WHEN'], ['Qty', 'M', 'BEFORE', 'WHEN'], ['AND', 'Qty', 'Form', 'Frequency', 'Period', 'PeriodUnit'], ['Qty', 'Form', 'Frequency', 'Period', 'PeriodUnit'], ['Qty', 'Form', 'Frequency', 'Period', 'PeriodUnit'], ['Qty', 'Form', 'Frequency', 'Period', 'PeriodUnit'], ['Qty', 'Form', 'Frequency', 'FOR', 'Duration', 'DurationUnit', 'THEN', 'Qty', 'Form', 'Frequency', 'PeriodUnit', 'AT', 'WHEN'], ['Qty', 'Form', 'Duration', 'DurationUnit', 'TID'], ['Method', 'Qty', 'Form', 'FOR', 'Duration', 'DurationUnit', 'Qty', 'TIMES', 'Period', 'PeriodUnit'], ['QID', 'Q6H'], ['BID'], ['QID'],['Qty', 'Form', 'BEFORE', 'WHEN', 'AND', 'WHEN'], ['Qty', 'Form', 'BEFORE', 'WHEN', 'AND', 'WHEN'], ['Method', 'Qty', 'Form', 'AT', 'WHEN'], ['Qty', 'Form', 'Frequency', 'DAILY', 'FOR', 'Duration', 'DurationUnit'], ['Qty', 'Form', 'FOR', 'Duration', 'DurationUnit', 'Frequency', 'TIMES', 'Period', 'PeriodUnit'], ['Method', 'Qty', 'Form', 'Period', 'PeriodUnit'], ['QID', 'FOR', 'Duration', 'DurationUnit'], ['EVERY', 'PeriodUnit'], ['Method', 'Qty', 'Form', 'AT', 'WHEN'], ['Method', 'Qty', 'Form', 'BEFORE', 'WHEN'], ['Method', 'Qty', 'Form', 'DAILY'], ['Method', 'Qty', 'Form', 'Frequency', 'Period', 'PeriodUnit'], ['Method', 'Qty', 'Form', 'Frequency', 'Period', 'PeriodUnit'], ['Method', 'DAILY'], ['Method', 'Qty', 'Form', 'BEFORE', 'WHEN'], ['EVERY', 'Period', 'PeriodUnit'], ['BEFORE', 'FOOD'], ['AFTER', 'FOOD'], ['FOR', 'Duration', 'DurationUnit'], ['FOR', 'Duration', 'DurationUnit'], ['WITH', 'FOOD']]

    whole_data= [[('for', 'FOR'), ('5', 'Duration'), ('to', 'TO'), ('6', 'DurationMax'), ('days', 'DurationUnit')], [('inject', 'Method'), ('2', 'Qty'), ('units', 'Form')], [('x', 'FOR'), ('2', 'Duration'), ('weeks', 'DurationUnit')], [('x', 'FOR'), ('3', 'Duration'), ('days', 'DurationUnit')], [('every', 'EVERY'), ('day', 'Period')], [('every', 'EVERY'), ('2', 'Period'), ('weeks', 'PeriodUnit')], [('every', 'EVERY'), ('3', 'Period'), ('days', 'PeriodUnit')], [('every', 'EVERY'), ('1', 'Period'), ('to', 'TO'), ('2', 'PeriodMax'), ('months', 'PeriodUnit')], [('every', 'EVERY'), ('2', 'Period'), ('to', 'TO'), ('6', 'PeriodMax'), ('weeks', 'PeriodUnit')], [('every', 'EVERY'), ('4', 'Period'), ('to', 'TO'), ('6', 'PeriodMax'), ('days', 'PeriodUnit')], [('take', 'Method'), ('two', 'Qty'), ('to', 'TO'), ('four', 'Qty'), ('tabs', 'Form')], [('take', 'Method'), ('2', 'Qty'), ('to', 'TO'), ('4', 'Qty'), ('tabs', 'Form')], [('take', 'Method'), ('3', 'Qty'), ('tabs', 'Form'), ('orally', 'PO'), ('bid', 'BID'), ('for', 'FOR'), ('10', 'Duration'), ('days', 'DurationUnit'), ('at', 'AT'), ('bedtime', 'WHEN')], [('swallow', 'Method'), ('three', 'Qty'), ('capsules', 'Form'), ('tid', 'TID'), ('orally', 'PO')], [('take', 'Method'), ('2', 'Qty'), ('capsules', 'Form'), ('po', 'PO'), ('every', 'EVERY'), ('6', 'Period'), ('hours', 'PeriodUnit')], [('take', 'Method'), ('2', 'Qty'), ('tabs', 'Form'), ('po', 'PO'), ('for', 'FOR'), ('10', 'Duration'), ('days', 'DurationUnit')], [('take', 'Method'), ('100', 'Qty'), ('caps', 'Form'), ('by', 'BY'), ('mouth', 'PO'), ('tid', 'TID'), ('for', 'FOR'), ('10', 'Duration'), ('weeks', 'DurationUnit')], [('take', 'Method'), ('2', 'Qty'), ('tabs', 'Form'), ('after', 'AFTER'), ('an', 'Period'), ('hour', 'PeriodUnit')], [('2', 'Qty'), ('tabs', 'Form'), ('every', 'EVERY'), ('4-6', 'Period'), ('hours', 'PeriodUnit')], [('every', 'EVERY'), ('4', 'Period'), ('to', 'TO'), ('6', 'PeriodMax'), ('hours', 'PeriodUnit')], [('q46h', 'Q46H')], [('q4-6h', 'Q4-6H')], [('2', 'Qty'), ('hours', 'PeriodUnit'), ('before', 'BEFORE'), ('breakfast', 'WHEN')], [('before', 'BEFORE'), ('30', 'Qty'), ('mins', 'M'), ('at', 'AT'), ('bedtime', 'WHEN')], [('30', 'Qty'), ('mins', 'M'), ('before', 'BEFORE'), ('bed', 'WHEN')], [('and', 'AND'), ('100', 'Qty'), ('tabs', 'Form'), ('twice', 'Frequency'), ('a', 'Period'), ('month', 'PeriodUnit')], [('100', 'Qty'), ('tabs', 'Form'), ('twice', 'Frequency'), ('a', 'Period'), ('month', 'PeriodUnit')], [('100', 'Qty'), ('tabs', 'Form'), ('once', 'Frequency'), ('a', 'Period'), ('month', 'PeriodUnit')], [('100', 'Qty'), ('tabs', 'Form'), ('thrice', 'Frequency'), ('a', 'Period'), ('month', 'PeriodUnit')], [('3', 'Qty'), ('tabs', 'Form'), ('daily', 'Frequency'), ('for', 'FOR'), ('3', 'Duration'), ('days', 'DurationUnit'), ('then', 'THEN'), ('1', 'Qty'), ('tab', 'Form'), ('per', 'Frequency'), ('day', 'PeriodUnit'), ('at', 'AT'), ('bed', 'WHEN')], [('30', 'Qty'), ('tabs', 'Form'), ('10', 'Duration'), ('days', 'DurationUnit'), ('tid', 'TID')], [('take', 'Method'), ('30', 'Qty'), ('tabs', 'Form'), ('for', 'FOR'), ('10', 'Duration'), ('days', 'DurationUnit'), ('three', 'Qty'), ('times', 'TIMES'), ('a', 'Period'), ('day', 'PeriodUnit')], [('qid', 'QID'), ('q6h', 'Q6H')], [('bid', 'BID')], [('qid', 'QID')], [('30', 'Qty'), ('tabs', 'Form'), ('before', 'BEFORE'), ('dinner', 'WHEN'), ('and', 'AND'), ('bedtime', 'WHEN')], [('30', 'Qty'), ('tabs', 'Form'), ('before', 'BEFORE'), ('dinner', 'WHEN'), ('&', 'AND'), ('bedtime', 'WHEN')], [('take', 'Method'), ('3', 'Qty'), ('tabs', 'Form'), ('at', 'AT'), ('bedtime', 'WHEN')], [('30', 'Qty'), ('tabs', 'Form'), ('thrice', 'Frequency'), ('daily', 'DAILY'), ('for', 'FOR'), ('10', 'Duration'), ('days', 'DurationUnit')], [('30', 'Qty'), ('tabs', 'Form'), ('for', 'FOR'), ('10', 'Duration'), ('days', 'DurationUnit'), ('three', 'Frequency'), ('times', 'TIMES'), ('a', 'Period'), ('day', 'PeriodUnit')], [('take', 'Method'), ('2', 'Qty'), ('tablets', 'Form'), ('a', 'Period'), ('day', 'PeriodUnit')], [('qid', 'QID'), ('for', 'FOR'), ('10', 'Duration'), ('days', 'DurationUnit')], [('every', 'EVERY'), ('day', 'PeriodUnit')], [('take', 'Method'), ('2', 'Qty'), ('caps', 'Form'), ('at', 'AT'), ('bedtime', 'WHEN')], [('apply', 'Method'), ('3', 'Qty'), ('drops', 'Form'), ('before', 'BEFORE'), ('bedtime', 'WHEN')], [('take', 'Method'), ('three', 'Qty'), ('capsules', 'Form'), ('daily', 'DAILY')], [('swallow', 'Method'), ('3', 'Qty'), ('pills', 'Form'), ('once', 'Frequency'), ('a', 'Period'), ('day', 'PeriodUnit')], [('swallow', 'Method'), ('three', 'Qty'), ('pills', 'Form'), ('thrice', 'Frequency'), ('a', 'Period'), ('day', 'PeriodUnit')], [('apply', 'Method'), ('daily', 'DAILY')], [('apply', 'Method'), ('three', 'Qty'), ('drops', 'Form'), ('before', 'BEFORE'), ('bedtime', 'WHEN')], [('every', 'EVERY'), ('6', 'Period'), ('hours', 'PeriodUnit')], [('before', 'BEFORE'), ('food', 'FOOD')], [('after', 'AFTER'), ('food', 'FOOD')], [('for', 'FOR'), ('20', 'Duration'), ('days', 'DurationUnit')], [('for', 'FOR'), ('twenty', 'Duration'), ('days', 'DurationUnit')], [('with', 'WITH'), ('meals', 'FOOD')]]
    sample_data = [[('for', 'IN', 'FOR'), ('5', 'CD', 'Duration'), ('to', 'TO', 'TO'), ('6', 'CD', 'DurationMax'), ('days', 'NNS', 'DurationUnit')],[('inject', 'NN', 'Method'), ('2', 'CD', 'Qty'), ('units', 'NNS', 'Form')],[('x', 'NN', 'FOR'),   ('2', 'CD', 'Duration'), ('weeks', 'NNS', 'DurationUnit')],[('x', 'NN', 'FOR'), ('3', 'CD', 'Duration'), ('days', 'NNS', 'DurationUnit')],[('every', 'DT', 'EVERY'), ('day', 'NN', 'Period')],[('every', 'DT', 'EVERY'),   ('2', 'CD', 'Period'), ('weeks', 'NNS', 'PeriodUnit')],[('every', 'DT', 'EVERY'), ('3', 'CD', 'Period'), ('days', 'NNS', 'PeriodUnit')],[('every', 'DT', 'EVERY'),   ('1', 'CD', 'Period'), ('to', 'TO', 'TO'), ('2', 'CD', 'PeriodMax'), ('months', 'NNS', 'PeriodUnit')],[('every', 'DT', 'EVERY'), ('2', 'CD', 'Period'), ('to', 'TO', 'TO'), ('6', 'CD', 'PeriodMax'), ('weeks', 'NNS', 'PeriodUnit')],[('every', 'DT', 'EVERY'),   ('4', 'CD', 'Period'), ('to', 'TO', 'TO'), ('6', 'CD', 'PeriodMax'), ('days', 'NNS', 'PeriodUnit')],[('take', 'VB', 'Method'), ('two', 'CD', 'Qty'), ('to', 'TO', 'TO'), ('four', 'CD', 'Qty'), ('tabs', 'NNS', 'Form')],[('take', 'VB', 'Method'),  ('2', 'CD', 'Qty'),  ('to', 'TO', 'TO'),  ('4', 'CD', 'Qty'),  ('tabs', 'NNS', 'Form')],[('take', 'VB', 'Method'),  ('3', 'CD', 'Qty'),  ('tabs', 'NNS', 'Form'),  ('orally', 'RB', 'PO'),  ('bid', 'NN', 'BID'),  ('for', 'IN', 'FOR'),  ('10', 'CD', 'Duration'),  ('days', 'NNS', 'DurationUnit'),  ('at', 'IN', 'AT'),  ('bedtime', 'NN', 'WHEN')],[('swallow', 'NN', 'Method'),  ('three', 'CD', 'Qty'),  ('capsules', 'NNS', 'Form'),  ('tid', 'NN', 'TID'),  ('orally', 'RB', 'PO')], [('take', 'VB', 'Method'),  ('2', 'CD', 'Qty'),  ('capsules', 'NNS', 'Form'),  ('po', 'NN', 'PO'),  ('every', 'DT', 'EVERY'),  ('6', 'CD', 'Period'),  ('hours', 'NNS', 'PeriodUnit')], [('take', 'VB', 'Method'),  ('2', 'CD', 'Qty'),  ('tabs', 'NNS', 'Form'),  ('po', 'NN', 'PO'),  ('for', 'IN', 'FOR'),  ('10', 'CD', 'Duration'),  ('days', 'NNS', 'DurationUnit')], [('take', 'VB', 'Method'),  ('100', 'CD', 'Qty'),  ('caps', 'NNS', 'Form'),  ('by', 'IN', 'BY'),  ('mouth', 'NN', 'PO'),  ('tid', 'NN', 'TID'),  ('for', 'IN', 'FOR'),  ('10', 'CD', 'Duration'),  ('weeks', 'NNS', 'DurationUnit')], [('take', 'VB', 'Method'),  ('2', 'CD', 'Qty'),  ('tabs', 'NNS', 'Form'),  ('after', 'IN', 'AFTER'),  ('an', 'DT', 'Period'),  ('hour', 'NN', 'PeriodUnit')], [('2', 'CD', 'Qty'),  ('tabs', 'NNS', 'Form'),  ('every', 'DT', 'EVERY'),  ('4-6', 'JJ', 'Period'),  ('hours', 'NNS', 'PeriodUnit')], [('every', 'DT', 'EVERY'),  ('4', 'CD', 'Period'),  ('to', 'TO', 'TO'),  ('6', 'CD', 'PeriodMax'),  ('hours', 'NNS', 'PeriodUnit')], [('q46h', 'NN', 'Q46H')],[('q4-6h', 'NN', 'Q4-6H')],[('2', 'CD', 'Qty'),  ('hours', 'NNS', 'PeriodUnit'),  ('before', 'IN', 'BEFORE'),  ('breakfast', 'NN', 'WHEN')],[('before', 'IN', 'BEFORE'),  ('30', 'CD', 'Qty'),  ('mins', 'NNS', 'M'),  ('at', 'IN', 'AT'),  ('bedtime', 'NN', 'WHEN')], [('30', 'CD', 'Qty'),  ('mins', 'NNS', 'M'),  ('before', 'IN', 'BEFORE'),  ('bed', 'NN', 'WHEN')],[('and', 'CC', 'AND'),  ('100', 'CD', 'Qty'),  ('tabs', 'NNS', 'Form'),  ('twice', 'RB', 'Frequency'),  ('a', 'DT', 'Period'),  ('month', 'NN', 'PeriodUnit')], [('100', 'CD', 'Qty'),  ('tabs', 'NNS', 'Form'),  ('twice', 'RB', 'Frequency'),  ('a', 'DT', 'Period'),  ('month', 'NN', 'PeriodUnit')],[('100', 'CD', 'Qty'),  ('tabs', 'NNS', 'Form'),  ('once', 'RB', 'Frequency'),  ('a', 'DT', 'Period'),  ('month', 'NN', 'PeriodUnit')],[('100', 'CD', 'Qty'),  ('tabs', 'NNS', 'Form'),  ('thrice', 'NN', 'Frequency'),  ('a', 'DT', 'Period'),  ('month', 'NN', 'PeriodUnit')], [('3', 'CD', 'Qty'),  ('tabs', 'NNS', 'Form'),  ('daily', 'JJ', 'Frequency'),  ('for', 'IN', 'FOR'),  ('3', 'CD', 'Duration'),  ('days', 'NNS', 'DurationUnit'),  ('then', 'RB', 'THEN'),  ('1', 'CD', 'Qty'),  ('tab', 'NN', 'Form'),  ('per', 'IN', 'Frequency'),  ('day', 'NN', 'PeriodUnit'),  ('at', 'IN', 'AT'),  ('bed', 'NN', 'WHEN')],[('30', 'CD', 'Qty'),  ('tabs', 'NNS', 'Form'),  ('10', 'CD', 'Duration'),  ('days', 'NNS', 'DurationUnit'),  ('tid', 'NN', 'TID')], [('take', 'VB', 'Method'),  ('30', 'CD', 'Qty'),  ('tabs', 'NNS', 'Form'),  ('for', 'IN', 'FOR'),  ('10', 'CD', 'Duration'),  ('days', 'NNS', 'DurationUnit'),  ('three', 'CD', 'Qty'),  ('times', 'NNS', 'TIMES'),  ('a', 'DT', 'Period'),  ('day', 'NN', 'PeriodUnit')],[('qid', 'NN', 'QID'), ('q6h', 'NN', 'Q6H')],[('bid', 'NN', 'BID')],[('qid', 'NN', 'QID')],[('30', 'CD', 'Qty'),  ('tabs', 'NNS', 'Form'),  ('before', 'IN', 'BEFORE'),  ('dinner', 'NN', 'WHEN'),  ('and', 'CC', 'AND'),  ('bedtime', 'NN', 'WHEN')], [('30', 'CD', 'Qty'),  ('tabs', 'NNS', 'Form'), ('before', 'IN', 'BEFORE'),  ('dinner', 'NN', 'WHEN'),  ('&', 'CC', 'AND'),  ('bedtime', 'NN', 'WHEN')],[('take', 'VB', 'Method'),  ('3', 'CD', 'Qty'),  ('tabs', 'NNS', 'Form'),  ('at', 'IN', 'AT'),  ('bedtime', 'NN', 'WHEN')], [('30', 'CD', 'Qty'),  ('tabs', 'NNS', 'Form'),  ('thrice', 'NN', 'Frequency'),  ('daily', 'JJ', 'DAILY'),  ('for', 'IN', 'FOR'),  ('10', 'CD', 'Duration'),  ('days', 'NNS', 'DurationUnit')], [('30', 'CD', 'Qty'),  ('tabs', 'NNS', 'Form'),  ('for', 'IN', 'FOR'),  ('10', 'CD', 'Duration'),  ('days', 'NNS', 'DurationUnit'),  ('three', 'CD', 'Frequency'),  ('times', 'NNS', 'TIMES'),  ('a', 'DT', 'Period'),  ('day', 'NN', 'PeriodUnit')],[('take', 'VB', 'Method'),  ('2', 'CD', 'Qty'),  ('tablets', 'NNS', 'Form'),  ('a', 'DT', 'Period'),  ('day', 'NN', 'PeriodUnit')], [('qid', 'NN', 'QID'),  ('for', 'IN', 'FOR'),  ('10', 'CD', 'Duration'),  ('days', 'NNS', 'DurationUnit')],[('every', 'DT', 'EVERY'), ('day', 'NN', 'PeriodUnit')],[('take', 'VB', 'Method'),  ('2', 'CD', 'Qty'),  ('caps', 'NNS', 'Form'),  ('at', 'IN', 'AT'),  ('bedtime', 'NN', 'WHEN')], [('apply', 'VB', 'Method'),  ('3', 'CD', 'Qty'),  ('drops', 'NNS', 'Form'),  ('before', 'IN', 'BEFORE'),  ('bedtime', 'NN', 'WHEN')], [('take', 'VB', 'Method'),  ('three', 'CD', 'Qty'),  ('capsules', 'NNS', 'Form'),  ('daily', 'JJ', 'DAILY')], [('swallow', 'NN', 'Method'),  ('3', 'CD', 'Qty'),  ('pills', 'NNS', 'Form'),  ('once', 'RB', 'Frequency'),  ('a', 'DT', 'Period'),  ('day', 'NN', 'PeriodUnit')], [('swallow', 'NN', 'Method'),  ('three', 'CD', 'Qty'),  ('pills', 'NNS', 'Form'),  ('thrice', 'NN', 'Frequency'),  ('a', 'DT', 'Period'),  ('day', 'NN', 'PeriodUnit')], [('apply', 'VB', 'Method'), ('daily', 'JJ', 'DAILY')], [('apply', 'VB', 'Method'),  ('three', 'CD', 'Qty'),  ('drops', 'NNS', 'Form'),  ('before', 'IN', 'BEFORE'),  ('bedtime', 'NN', 'WHEN')], [('every', 'DT', 'EVERY'),  ('6', 'CD', 'Period'),  ('hours', 'NNS', 'PeriodUnit')],[('before', 'IN', 'BEFORE'), ('food', 'NN', 'FOOD')], [('after', 'IN', 'AFTER'), ('food', 'NN', 'FOOD')], [('for', 'IN', 'FOR'),  ('20', 'CD', 'Duration'),  ('days', 'NNS', 'DurationUnit')], [('for', 'IN', 'FOR'),  ('twenty', 'NN', 'Duration'),  ('days', 'NNS', 'DurationUnit')],  [('with', 'IN', 'WITH'), ('meals', 'NNS', 'FOOD')]] 
    
    data = json.loads(request.body.decode("utf-8"))
    search = data["search"]
    resdf = pd.DataFrame()
    res = return_result(search,resdf)
    print(res)
    return render(request,"result.html") 

@csrf_exempt
def sur_risk(request):
    data = json.loads(request.body.decode("utf-8"))
    
    age=int(data["age"])
    emergency=int(data["emer"])
    ventilator=int(data["vent"])
    cancer=int(data["cancer"])
    diabetes=int(data["diab"])
    hypertension=int(data["hypt"])
    dialysis=int(data["dial"])
    renalval=int(data["ren"])
    weight=int(data["wt"])
    height=int(data["ht"])
    try:
        val=[]
        serious=0
        compl=0
        cardiac=0
        infection=0
        renal=0
        readmission=0
        returnOR=0
        los=0
        if(age<65):
            cardiac+=0.2
            serious+=0.2
            compl+=0.4
            infection+=0.2
            readmission+=0.2
        elif(age>=65 & age<74):
            serious+=0.4
            compl+=0.5
            cardiac+=0.2
            infection+=0.2
            readmission+=0.2
        elif(age>=75):
            serious+=0.6
            compl+=0.6
            cardiac+=0.4
            renal+= 0.2
            infection+=0.3
            readmission+=0.3
            returnOR=0.3
        if(emergency==1):
            serious+=0.4
            infection+=0.3
            returnOR+=0.3
            readmission+=0.2
            compl+=0.4
        if(ventilator==1):
            serious+=0.5
            compl+=0.4
            cardiac+=0.4
            readmission+=0.5
        if(cancer==1):
            cardiac+=0.3
            readmission+=0.4
            returnOR+=0.4
        if(diabetes==1):
            serious+=0.4
            compl+=0.4
            infection+=0.5
            renal+=0.4
            returnOR+=0.4
        if(hypertension==1):
            serious+=0.3
            compl+=0.3
            cardiac+=0.3
            infection+=0.5
        if(dialysis==1):
            serious+=0.4
            compl+=0.4
            renal+=0.4
            infection+=0.1
        if(renalval==1):
            serious+=0.2
            compl+=0.2
            renal+=0.2
            infection+=0.4
        
        bmi = BMI(height, weight)
        if (bmi < 18.5):
            serious+=0.5
            compl+=0.5
            cardiac+=0.5
            renal+= 0.4
            infection+=0.4
            readmission+=0.4
            returnOR=0.4
        elif ( bmi >= 18.5 and bmi < 24.9):
            serious+=0.3
            compl+=0.3
            cardiac+=0.3
            renal+= 0.3
            infection+=0.3
            readmission+=0.2
            returnOR=0.1
        elif ( bmi >= 24.9 and bmi < 30):
            serious+=0.6
            compl+=0.5
            cardiac+=0.6
            renal+= 0.3
            infection+=0.3
            readmission+=0.3
            returnOR=0.3
        elif( bmi >=30):
            serious+=0.7
            compl+=0.6
            cardiac+=0.6
            renal+= 0.4
            infection+=0.4
            readmission+=0.4
            returnOR=0.4
        
        val.append(serious)
        val.append(compl)
        val.append(cardiac)
        val.append(infection)
        val.append(renal)
        val.append(readmission)
        val.append(returnOR)
        avg = Average(val)
        if(avg<1):
            los+=1
        elif(avg>1 and avg<4):
            los+=2
        elif(avg>4 and avg<10):
            los+=5
        elif(avg>10):
            los+=7
        val.append(los)
        return JsonResponse({"res":val})
    except:
        return JsonResponse({"res":[-1]})




# # ===================================================
# #              HELPER FUNCTIONS
# # ===================================================

def token_to_features(doc, i):
    word = doc[i][0]
    postag = doc[i][1]
    features = [
        'bias',
        'word.lower=' + word.lower(),
        'word[-3:]=' + word[-3:],
        'word[-2:]=' + word[-2:],
        'word.isupper=%s' % word.isupper(),
        'word.istitle=%s' % word.istitle(),
        'word.isdigit=%s' % word.isdigit(),
        'postag=' + postag
    ]
    if i > 0:
        word1 = doc[i-1][0]
        postag1 = doc[i-1][1]
        features.extend([
            '-1:word.lower=' + word1.lower(),
            '-1:word.istitle=%s' % word1.istitle(),
            '-1:word.isupper=%s' % word1.isupper(),
            '-1:word.isdigit=%s' % word1.isdigit(),
            '-1:postag=' + postag1
        ])
    else:
        features.append('BOS')
    if i < len(doc)-1:
        word1 = doc[i+1][0]
        postag1 = doc[i+1][1]
        features.extend([
            '+1:word.lower=' + word1.lower(),
            '+1:word.istitle=%s' % word1.istitle(),
            '+1:word.isupper=%s' % word1.isupper(),
            '+1:word.isdigit=%s' % word1.isdigit(),
            '+1:postag=' + postag1
        ])
    else:
        features.append('EOS')
    return features

def get_features(doc):
    return [token_to_features(doc, i) for i in range(len(doc))]

def get_labels(doc):
    return [label for (token, postag, label) in doc]


def predict(sig):
    demo = []
    sample_data = []
    sig = [sig]
    for x in sig:
        temp = nltk.word_tokenize(x)
        pos = nltk.pos_tag(temp)
        for y in range(len(pos)):
            temp2 = (pos[y][0], pos[y][1], pos[y][1]) 
            demo.append(temp2) 
            sample_data.append(demo)
            demo = []
    data = [get_features(doc) for doc in sample_data]
    predictions = [tagger.tag(xseq) for xseq in data]
    
    return predictions

def return_result(s, resdf):
  pred = predict(s) 

  sent = s.split(" ")
  len(sent)
  entity = []
  for i in range(len(pred)):
      entity.append(pred[i][0])
  len(entity)
      
  resdf['entity'] = entity
  resdf['value'] = sent

  return resdf

def BMI(height, weight):
    bmi = weight/(height**2)
    return bmi

def Average(lst):
    return sum(lst) / len(lst)

