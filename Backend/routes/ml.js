const express = require("express");
const app = express();
const router = express.Router();
const axios = require('axios');


// @route   GET logout/
// @desc    Logs out the current user
// @access  Public
router.get("/cost_pred", function (req, res) {

encounters = ["ambulatory", "emergency", "outpatient", "inpatient", "wellness"];
hospitals = ["CAMBRIDGE HEALTH ALLIANCE","HOLYOKE MEDICAL CENTER","LOWELL GENERAL HOSPITAL","BRIGHAM AND WOMEN'S HOSPITAL","ST ELIZABETH'S MEDICAL CENTER","MOUNT AUBURN HOSPITAL","BETH ISRAEL DEACONESS HOSPITAL - PLYMOUTH","BAYSTATE MEDICAL CENTER","SHRINERS' HOSPITAL FOR CHILDREN (THE)","SAINT ANNE'S HOSPITAL","SOUTHCOAST HOSPITAL GROUP  INC","NORWOOD HOSPITAL","NEWTON-WELLESLEY HOSPITAL","SOUTH SHORE HOSPITAL","BETH ISRAEL DEACONESS HOSPITAL-MILTON INC","NEW ENGLAND BAPTIST HOSPITAL","CARNEY HOSPITAL","LAHEY HOSPITAL & MEDICAL CENTER  BURLINGTON","SIGNATURE HEALTHCARE BROCKTON HOSPITAL","METROWEST MEDICAL CENTER","HALLMARK HEALTH SYSTEM","NORTH SHORE MEDICAL CENTER -","HALLMARK HEALTH MEDICAL ASSOCIATES INC","BROCKTON AREA MULTI-SERVICES  INC.","GOOD SAMARITAN MEDICAL CENTER","MILFORD REGIONAL MEDICAL CENTER","HEALTHALLIANCE HOSPITALS  INC","BAYSTATE FRANKLIN MEDICAL CENTER","MASSACHUSETTS GENERAL HOSPITAL","WINCHESTER HOSPITAL","ANNA JAQUES HOSPITAL","BETH ISRAEL DEACONESS HOSPITAL - NEEDHAM","COOLEY DICKINSON HOSPITAL INC THE","BOSTON CHILDREN'S HOSPITAL","BOSTON MEDICAL CENTER CORPORATION-","MORTON HOSPITAL","MARLBOROUGH HOSPITAL","MERCY MEDICAL CTR","CAPE COD HOSPITAL","BEVERLY HOSPITAL CORPORATION","NOBLE HOSPITAL","PCP89345","PCP128586","HARRINGTON MEMORIAL HOSPITAL-1","Plymouth Outreach Clinic","AT CARE PLLC","Edith Nourse Rogers Memorial Veterans Hospital (Bedford VA)","HEYWOOD HOSPITAL -","UMASS MEMORIAL MEDICAL CENTER INC","ST VINCENT HOSPITAL","ADCARE HOSPITAL OF WORCESTER INC","PCP205980","STURDY MEMORIAL HOSPITAL","NANTUCKET COTTAGE HOSPITAL","MASSACHUSETTS EYE AND EAR INFIRMARY -","BRIGHAM AND WOMEN'S FAULKNER HOSPITAL","LAWRENCE GENERAL HOSPITAL","BETH ISRAEL DEACONESS MEDICAL CENTER","TUFTS MEDICAL CENTER","EMERSON HOSPITAL -","Hyannis Outpatient Clinic","COUNSELING ASSOCIATES OF DRACUT AND METHUEN","CLINTON HOSPITAL ASSOCIATION","Quincy Outpatient Clinic","ORTHOPEDIC AND SPORTS PHYSICAL THERAPY  LLP","FRANCISCAN CHILDREN'S HOSPITAL & REHAB CENTER","FALMOUTH HOSPITAL","PCP26110","HOLY FAMILY HOSPITAL","UHS OF WESTWOOD PEMBROKE INC","BERKSHIRE MEDICAL CENTER INC - 1","Framingham Outpatient Clinic","REHAB RESOLUTIONS INC","NEW ENGLAND ORAL SURGERY ASSOCIATES LLC","BAYSTATE WING HOSPITAL AND MEDICAL CENTERS","PCP44465","PCP136067","SOUTH BAY MENTAL HEALTH CENTER  INC.","PCP10127","VA Boston Healthcare System  Jamaica Plain Campus","Worcester Outpatient Clinic","PCP166697","CAREWELL URGENT CARE CENTERS OF MA  PC","Worcester Vet Center","FAIRVIEW HOSPITAL","Gloucester Community Based Outpatient Clinic (CBOC)","Lowell Outpatient Clinic","PCP191696","PCP67787","PCP139219","Boston Vet Center","Haverhill Community Based Outpatient Clinic (CBOC)","NASHOBA VALLEY MEDICAL CENTER","SHRINERS' HOSPITAL FOR CHILDREN - BOSTON  THE","RIVERSIDE RADIOLOGY MEDICAL GROUP INC","ADAMS PHYSICAL THERAPY  LLC","DENTAL SURGEONS OF FALL RIVER PC","Fitchburg Outpatient Clinic","PCP4453","PCP9047","New Bedford Outpatient Clinic","Springfield Vet Center","MARTHA'S VINEYARD HOSPITAL INC","PCP13802","New Bedford Vet Center","ATHOL MEMORIAL HOSPITAL","PCP52699","PCP77608","VA Boston Healthcare System  Brockton Campus","PCP3184","PCP26077","PCP118611","CAMBRIDGE PUBLIC HEALTH COMMISSION","HAMPDEN PODIATRY ASSOCIATES","SOUTH SHORE RADIOLOGICAL ASSOCIATES  INC.","HEBREW REHABILITATION CENTER","MILTON CHIROPRACTIC AND REHABILITATION INC","MERRIMACK VALLEY PHYSICAL THERAPY"];
description = ["Respiratory therapy","Wound care","Fracture care","Asthma self management","Physical therapy procedure","Routine antenatal care","Urinary tract infection care","Demential management","Diabetes self management plan","Head injury rehabilitation","Lifestyle education regarding hypertension","Cancer care plan","Chronic obstructive pulmonary disease clinical management plan","Psychiatry care plan","Care Plan","Hyperlipidemia clinical management plan"];
reason = ["Acute bronchitis (disorder)","Facial laceration","Fracture of ankle","Laceration of foot","Childhood asthma","Laceration of forearm","Tear of meniscus of knee","Fracture of forearm","Laceration of thigh","Injury of medial collateral ligament of knee","Normal pregnancy","Injury of anterior cruciate ligament","Fracture subluxation of wrist","Laceration of hand","Fracture of clavicle","Fracture of rib","Closed fracture of hip","Escherichia coli urinary tract infection","Alzheimer\'s disease (disorder)","Prediabetes","Bullet wound","Cystitis","Rupture of patellar tendon","Sprain of ankle","Concussion with no loss of consciousness","Hypertension","Familial Alzheimer\'s disease of early onset (disorder)","Malignant tumor of colon","Pulmonary emphysema (disorder)","Major depression disorder","Chronic obstructive bronchitis (disorder)","Neoplasm of prostate","Diabetes","Hyperlipidemia"];
diagnosis = ["Measurement of respiratory function (procedure)","Suture open wound","Bone immobilization","Ankle X-ray","Plain chest X-ray (procedure)","Asthma screening","Sputum examination (procedure)","Knee X-ray","Upper arm X-ray","Injection of tetanus antitoxin","Urine culture","Urine protein test","Skin test for tuberculosis","Physical examination of mother","Measurement of Varicella-zoster virus antibody","Gonorrhea infection test","Chlamydia antigen test","Human immunodeficiency virus antigen test","Rubella screening","Hepatitis B Surface Antigen Measurement","Hemoglobin / Hematocrit / Platelet count","Blood typing  RH typing","Evaluation of uterine fundal height","Ultrasound scan for fetal viability","Syphilis infection test","Auscultation of the fetal heart","Standard pregnancy test","Hepatitis C antibody test","Urine screening test for diabetes","Cytopathology procedure  preparation of smear  genital source","Bone density scan (procedure)","X-ray or wrist","Medication Reconciliation (procedure)","Admission to orthopedic department","Clavicle X-ray","Chest X-ray","Pelvis X-ray","Alpha-fetoprotein test","Fetal anatomy study","Electrical cardioversion","Spirometry (procedure)","Augmentation of labor","Childbirth","Admission to trauma surgery department","High resolution computed tomography of chest without contrast (procedure)","Hearing examination (procedure)","Combined chemotherapy and radiation therapy (procedure)","Intramuscular injection","Extraction of wisdom tooth","positive screening for PHQ-9","Prostatectomy","Digital examination of rectum","Pulmonary rehabilitation (regime/therapy)"];
    res.render("cost_pred",{encounters,hospitals,description,reason,diagnosis});
});

router.post("/cost_pred",async (req,res)=>{
    try{
        const {enc,hosp,desc,rsn,days,diag} = req.body;
        const result = await axios("http://localhost:8000/cost_pred/",{
            method:"POST",
            data:{
                enc:enc,
                hosp:hosp,
                desc:desc,
                rsn:rsn,
                diag:diag,
                days:days
            },
            headers: {
                'Content-Type': 'application/json',
            }
        })
        console.log(result.data);
        const pred = result.data.res;
        console.log(pred)
        res.send("<h1>pred</h1>");
    }catch(err){
        res.send(err);
    }
    
})

module.exports = router;
