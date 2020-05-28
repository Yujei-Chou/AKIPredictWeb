import json
from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
import pandas as pd
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage

from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.contrib import auth
import xgboost as xgb
from xgboost import XGBClassifier
import os
import numpy as np
import pickle
import glob


def ReplaceNan(l):
    for i,data in enumerate(l):
        if(data == ''):
            l[i] = '-10000'
    return l


# Create your views here.
def startpage(req):
    return render(req, 'startPage.html')

def testunflod(req):
    return render(req, 'testUnflod.html')

@login_required
def homepage(req):
    return render(req, 'homepage.html')

def login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/homepage/')

    username = request.POST.get('username', '')
    password = request.POST.get('password', '')

    user = auth.authenticate(username=username, password=password)

    if user is not None and user.is_active:
        auth.login(request, user)
        return HttpResponseRedirect('/homepage/')
    else:
        return render(request, "login.html")


def logout(request):
    auth.logout(request)
    return render(request, "logout.html")

@login_required
def predictsingle(req):
    return render(req, 'predictSingle.html')

@login_required
def predictfile(req):
    return render(req, 'predictFile.html')

@login_required
def predict(request):
    Crt = []
    Intake = []
    Urine = []
    pH = []
    Hct = []
    BUN = []
    Na = []
    K = []
    TP = []
    SystolicBP = []
    MeanBP = []
    MSI = []
    eGFR = []

    Age = []
    Weight = []
    Gender = ""
    temp = []
    PredictRes = ""

    Agestr = ""
    Weightstr = ""
    Genderstr = ""

    filename = 'static/Xgboost_Seq.sav'
    Xgb_model = pickle.load(open(filename, 'rb'))
    if request.method == 'POST':
        if 'OnlyOneData' in request.POST:
            state = 'OnlyOneData'
            Age = request.POST['Age']
            Agestr = request.POST['Age']
            Weight = request.POST['Weight']
            Weightstr = request.POST['Weight']
            Gender = request.POST['Gender']
            Genderstr = request.POST['Gender']
            for i in range(0, 6):
                Crtstr = 'Crt_' + str(i)
                Intakestr = 'Intake_' + str(i)
                Urinestr = 'Urine_' + str(i)
                pHstr = 'pH_' + str(i)
                Hctstr = 'Hct_' + str(i)
                BUNstr = 'BUN_' + str(i)
                Nastr = 'Na_' + str(i)
                Kstr = 'K_' + str(i)
                TPstr = 'TP_' + str(i)
                SystolicBPstr = 'SystolicBP_' + str(i)
                MeanBPstr = 'MeanBP_' + str(i)
                MSIstr = 'MSI_' + str(i)
                eGFRstr = 'eGFR_' + str(i)

                Crt.append(request.POST[Crtstr])
                Intake.append(request.POST[Intakestr])
                Urine.append(request.POST[Urinestr])
                pH.append(request.POST[pHstr])
                Hct.append(request.POST[Hctstr])
                BUN.append(request.POST[BUNstr])
                Na.append(request.POST[Nastr])
                K.append(request.POST[Kstr])
                TP.append(request.POST[TPstr])
                SystolicBP.append(request.POST[SystolicBPstr])
                MeanBP.append(request.POST[MeanBPstr])
                MSI.append(request.POST[MSIstr])
                eGFR.append(request.POST[eGFRstr])

            Crt = list(map(float, ReplaceNan(Crt)))
            Intake = list(map(float, ReplaceNan(Intake)))
            Urine = list(map(float, ReplaceNan(Urine)))
            pH = list(map(float, ReplaceNan(pH)))
            Hct = list(map(float, ReplaceNan(Hct)))
            BUN = list(map(float, ReplaceNan(BUN)))
            Na = list(map(float, ReplaceNan(Na)))
            K = list(map(float, ReplaceNan(K)))
            TP = list(map(float, ReplaceNan(TP)))
            SystolicBP = list(map(float, ReplaceNan(SystolicBP)))
            MeanBP = list(map(float, ReplaceNan(MeanBP)))
            MSI = list(map(float, ReplaceNan(MSI)))
            eGFR = list(map(float, ReplaceNan(eGFR)))
            if (Gender == 'F'):
                Gender = '0'
            if (Gender == 'M'):
                Gender = '1'
            if (Gender == ''):
                Gender = '-10000'
            if (Weight == ''):
                Weight = '-10000'
            if (Age == ''):
                Age = '-10000'

            X = np.array([Crt, Intake, Urine, pH, Hct, BUN, Na, K, TP, SystolicBP, MeanBP, MSI, eGFR])
            X = X.reshape(1, -1)
            X = np.insert(X, 0, float(Gender), axis=1)
            X = np.insert(X, 0, float(Weight), axis=1)
            X = np.insert(X, 0, float(Age), axis=1)
            Y = Xgb_model.predict(X)

    context = {
        'PredictRes': PredictRes,
        'Crt': Crt, 'Intake': Intake, 'Urine': Urine, 'pH': pH, 'Hct': Hct, 'BUN': BUN,
        'Na': Na, 'K': K, 'TP': TP, 'SystolicBP': SystolicBP, 'MeanBP': MeanBP, 'MSI': MSI, 'eGFR': eGFR,
        'Agestr': Agestr, 'Weightstr': Weightstr, 'Genderstr': Genderstr,
    }
    return render(request, "prfip.html", context)

@login_required
def predictresultforinput(request):
    Crt = []
    Intake = []
    Urine = []
    pH = []
    Hct = []
    BUN = []
    Na = []
    K = []
    TP = []
    SystolicBP = []
    MeanBP = []
    MSI = []
    eGFR = []

    Age = []
    Weight = []
    Gender = ""
    temp = []
    PredictRes = ""

    Agestr = ""
    Weightstr = ""
    Genderstr = ""

    filename = 'static/Xgboost_Seq.sav'
    Xgb_model = pickle.load(open(filename, 'rb'))
    if request.method == 'POST':
        if 'OnlyOneData' in request.POST:
            state = 'OnlyOneData'
            Age = request.POST['Age']
            Agestr = request.POST['Age']
            Weight = request.POST['Weight']
            Weightstr = request.POST['Weight']
            Gender = request.POST['Gender']
            Genderstr = request.POST['Gender']
            for i in range(0, 6):
                Crtstr = 'Crt_' + str(i)
                Intakestr = 'Intake_' + str(i)
                Urinestr = 'Urine_' + str(i)
                pHstr = 'pH_' + str(i)
                Hctstr = 'Hct_' + str(i)
                BUNstr = 'BUN_' + str(i)
                Nastr = 'Na_' + str(i)
                Kstr = 'K_' + str(i)
                TPstr = 'TP_' + str(i)
                SystolicBPstr = 'SystolicBP_' + str(i)
                MeanBPstr = 'MeanBP_' + str(i)
                MSIstr = 'MSI_' + str(i)
                eGFRstr = 'eGFR_' + str(i)

                Crt.append(request.POST[Crtstr])
                Intake.append(request.POST[Intakestr])
                Urine.append(request.POST[Urinestr])
                pH.append(request.POST[pHstr])
                Hct.append(request.POST[Hctstr])
                BUN.append(request.POST[BUNstr])
                Na.append(request.POST[Nastr])
                K.append(request.POST[Kstr])
                TP.append(request.POST[TPstr])
                SystolicBP.append(request.POST[SystolicBPstr])
                MeanBP.append(request.POST[MeanBPstr])
                MSI.append(request.POST[MSIstr])
                eGFR.append(request.POST[eGFRstr])

            Crt = list(map(float, ReplaceNan(Crt)))
            Intake = list(map(float, ReplaceNan(Intake)))
            Urine = list(map(float, ReplaceNan(Urine)))
            pH = list(map(float, ReplaceNan(pH)))
            Hct = list(map(float, ReplaceNan(Hct)))
            BUN = list(map(float, ReplaceNan(BUN)))
            Na = list(map(float, ReplaceNan(Na)))
            K = list(map(float, ReplaceNan(K)))
            TP = list(map(float, ReplaceNan(TP)))
            SystolicBP = list(map(float, ReplaceNan(SystolicBP)))
            MeanBP = list(map(float, ReplaceNan(MeanBP)))
            MSI = list(map(float, ReplaceNan(MSI)))
            eGFR = list(map(float, ReplaceNan(eGFR)))
            if (Gender == 'F'):
                Gender = '0'
            if (Gender == 'M'):
                Gender = '1'
            if (Gender == ''):
                Gender = '-10000'
            if (Weight == ''):
                Weight = '-10000'
            if (Age == ''):
                Age = '-10000'

            X = np.array([Crt, Intake, Urine, pH, Hct, BUN, Na, K, TP, SystolicBP, MeanBP, MSI, eGFR])
            X = X.reshape(1, -1)
            X = np.insert(X, 0, float(Gender), axis=1)
            X = np.insert(X, 0, float(Weight), axis=1)
            X = np.insert(X, 0, float(Age), axis=1)
            Y = Xgb_model.predict(X)

    context = {
        'PredictRes': PredictRes,
        'aki' : Y,
        'Crt': Crt, 'Intake': Intake, 'Urine': Urine, 'pH': pH, 'Hct': Hct, 'BUN': BUN,
        'Na': Na, 'K': K, 'TP': TP, 'SystolicBP': SystolicBP, 'MeanBP': MeanBP, 'MSI': MSI, 'eGFR': eGFR,
        'Agestr': Agestr, 'Weightstr': Weightstr, 'Genderstr': Genderstr,
    }
    return render(request, "PredictResultForInput.html", context)

@login_required
def predictresultforfile(request):
    # Xgb_model = xgb.Booster(model_file=filename)
    if request.method == 'POST':
        if 'Upload' in request.POST:
            state = 'Upload'
            UploadFile = request.FILES['document']
            fs = FileSystemStorage()
            fs.save('./static/media/File', UploadFile)
            for filename in os.listdir("./static/media"):
                if (filename != "File"):
                    file = "./static/media/" + filename
                    os.remove(file)
    File_df = pd.read_csv('./static/media/File', sep=',', header=0, encoding='utf-8')
    test = File_df.fillna(-10000)
    X = test.to_numpy()
    filename = './static/Xgboost_Seq.sav'
    Xgb_model = pickle.load(open(filename, 'rb'))
    Y = Xgb_model.predict(X)
    # Y = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    File_df['AKI'] = Y
    numberPatient = []
    i = 0
    while i < len(Y):
        if Y[i] == 1:
            pair = [i+1,"AKI"]
        else:
            pair = [i + 1, "No AKI"]
        if (i+1) < len(Y) and Y[i + 1] == 1:
            pair.append(i+2)
            pair.append("AKI")
        elif (i+1) < len(Y) and Y[i + 1] == 0:
            pair.append(i + 2)
            pair.append("No AKI")
        if (i+2) < len(Y) and Y[i + 2] == 1:
            pair.append(i+3)
            pair.append("AKI")
        elif (i+2) < len(Y) and Y[i + 2] == 0:
            pair.append(i + 3)
            pair.append("No AKI")
        if (i+3) < len(Y) and Y[i + 3] == 1:
            pair.append(i+4)
            pair.append("AKI")
        elif (i+3) < len(Y) and Y[i + 3] == 0:
            pair.append(i + 4)
            pair.append("No AKI")
        i += 4
        numberPatient.append(pair)

    res = []
    for i in range(0, len(File_df)):
        DictTemp = {
            'age': File_df['age'][i],
            'weight': File_df['weight'][i],
            'gender': File_df['gender'].map({1: "M", 0: "F"})[i],
            'crt': File_df.loc[
                i, ['creatinine_seq_0', 'creatinine_seq_1', 'creatinine_seq_2', 'creatinine_seq_3', 'creatinine_seq_4',
                    'creatinine_seq_5']].tolist(),
            'intake': File_df.loc[i, ['intake_seq_0', 'intake_seq_1', 'intake_seq_2', 'intake_seq_3', 'intake_seq_4',
                                      'intake_seq_5']].tolist(),
            'urine': File_df.loc[
                i, ['urine_seq_0', 'urine_seq_1', 'urine_seq_2', 'urine_seq_3', 'urine_seq_4', 'urine_seq_5']].tolist(),
            'pH': File_df.loc[i, ['pH_seq_0', 'pH_seq_1', 'pH_seq_2', 'pH_seq_3', 'pH_seq_4', 'pH_seq_5']].tolist(),
            'Hct': File_df.loc[
                i, ['Hct_seq_0', 'Hct_seq_1', 'Hct_seq_2', 'Hct_seq_3', 'Hct_seq_4', 'Hct_seq_5']].tolist(),
            'BUN': File_df.loc[
                i, ['BUN_seq_0', 'BUN_seq_1', 'BUN_seq_2', 'BUN_seq_3', 'BUN_seq_4', 'BUN_seq_5']].tolist(),
            'Na': File_df.loc[i, ['Na_seq_0', 'Na_seq_1', 'Na_seq_2', 'Na_seq_3', 'Na_seq_4', 'Na_seq_5']].tolist(),
            'K': File_df.loc[i, ['K_seq_0', 'K_seq_1', 'K_seq_2', 'K_seq_3', 'K_seq_4', 'K_seq_5']].tolist(),
            'TP': File_df.loc[i, ['TP_seq_0', 'TP_seq_1', 'TP_seq_2', 'TP_seq_3', 'TP_seq_4', 'TP_seq_5']].tolist(),
            'systolicBP': File_df.loc[
                i, ['systolicBP_seq_0', 'systolicBP_seq_1', 'systolicBP_seq_2', 'systolicBP_seq_3', 'systolicBP_seq_4',
                    'systolicBP_seq_5']].tolist(),
            'meanBP': File_df.loc[i, ['meanBP_seq_0', 'meanBP_seq_1', 'meanBP_seq_2', 'meanBP_seq_3', 'meanBP_seq_4',
                                      'meanBP_seq_5']].tolist(),
            'MSI': File_df.loc[
                i, ['MSI_seq_0', 'MSI_seq_1', 'MSI_seq_2', 'MSI_seq_3', 'MSI_seq_4', 'MSI_seq_5']].tolist(),
            'eGFR': File_df.loc[
                i, ['eGFR_seq_0', 'eGFR_seq_1', 'eGFR_seq_2', 'eGFR_seq_3', 'eGFR_seq_4', 'eGFR_seq_5']].tolist(),
            'aki': File_df['AKI'][i],
        }
        res.append(DictTemp)

    paginator = Paginator(res, 1)
    page = request.GET.get('page')
    contacts = paginator.get_page(page)

    context = {
        'contacts': contacts,
        'all':Y,
        'count':numberPatient,
    }
    return render(request, "PredictResultForFile.html", context)

@login_required
def overview(request):
    # Xgb_model = xgb.Booster(model_file=filename)
    if request.method == 'POST':
        if 'Upload' in request.POST:
            state = 'Upload'
            UploadFile = request.FILES['document']
            fs = FileSystemStorage()
            fs.save('./static/media/File', UploadFile)
            for filename in os.listdir("./static/media"):
                if (filename != "File"):
                    file = "./static/media/" + filename
                    os.remove(file)
    File_df = pd.read_csv('./static/media/File', sep=',', header=0, encoding='utf-8')
    test = File_df.fillna(-10000)
    X = test.to_numpy()
    filename = './static/Xgboost_Seq.sav'
    Xgb_model = pickle.load(open(filename, 'rb'))
    Y = Xgb_model.predict(X)
    # Y = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    File_df['AKI'] = Y
    res = []
    for i in range(0, len(File_df)):
        DictTemp = {
            'age': File_df['age'][i],
            'weight': File_df['weight'][i],
            'gender': File_df['gender'].map({1: "M", 0: "F"})[i],
            'crt': File_df.loc[
                i, ['creatinine_seq_0', 'creatinine_seq_1', 'creatinine_seq_2', 'creatinine_seq_3', 'creatinine_seq_4',
                    'creatinine_seq_5']].tolist(),
            'intake': File_df.loc[i, ['intake_seq_0', 'intake_seq_1', 'intake_seq_2', 'intake_seq_3', 'intake_seq_4',
                                      'intake_seq_5']].tolist(),
            'urine': File_df.loc[
                i, ['urine_seq_0', 'urine_seq_1', 'urine_seq_2', 'urine_seq_3', 'urine_seq_4', 'urine_seq_5']].tolist(),
            'pH': File_df.loc[i, ['pH_seq_0', 'pH_seq_1', 'pH_seq_2', 'pH_seq_3', 'pH_seq_4', 'pH_seq_5']].tolist(),
            'Hct': File_df.loc[
                i, ['Hct_seq_0', 'Hct_seq_1', 'Hct_seq_2', 'Hct_seq_3', 'Hct_seq_4', 'Hct_seq_5']].tolist(),
            'BUN': File_df.loc[
                i, ['BUN_seq_0', 'BUN_seq_1', 'BUN_seq_2', 'BUN_seq_3', 'BUN_seq_4', 'BUN_seq_5']].tolist(),
            'Na': File_df.loc[i, ['Na_seq_0', 'Na_seq_1', 'Na_seq_2', 'Na_seq_3', 'Na_seq_4', 'Na_seq_5']].tolist(),
            'K': File_df.loc[i, ['K_seq_0', 'K_seq_1', 'K_seq_2', 'K_seq_3', 'K_seq_4', 'K_seq_5']].tolist(),
            'TP': File_df.loc[i, ['TP_seq_0', 'TP_seq_1', 'TP_seq_2', 'TP_seq_3', 'TP_seq_4', 'TP_seq_5']].tolist(),
            'systolicBP': File_df.loc[
                i, ['systolicBP_seq_0', 'systolicBP_seq_1', 'systolicBP_seq_2', 'systolicBP_seq_3', 'systolicBP_seq_4',
                    'systolicBP_seq_5']].tolist(),
            'meanBP': File_df.loc[i, ['meanBP_seq_0', 'meanBP_seq_1', 'meanBP_seq_2', 'meanBP_seq_3', 'meanBP_seq_4',
                                      'meanBP_seq_5']].tolist(),
            'MSI': File_df.loc[
                i, ['MSI_seq_0', 'MSI_seq_1', 'MSI_seq_2', 'MSI_seq_3', 'MSI_seq_4', 'MSI_seq_5']].tolist(),
            'eGFR': File_df.loc[
                i, ['eGFR_seq_0', 'eGFR_seq_1', 'eGFR_seq_2', 'eGFR_seq_3', 'eGFR_seq_4', 'eGFR_seq_5']].tolist(),
            'aki': File_df['AKI'][i],
        }
        res.append(DictTemp)

    paginator = Paginator(res, 1)
    page = request.GET.get('page')
    contacts = paginator.get_page(page)

    context = {
        'contacts': contacts,
    }
    return render(request, "overview.html", context)