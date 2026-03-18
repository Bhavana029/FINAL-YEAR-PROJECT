from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
from datetime import datetime
import os
import urllib.request
import tempfile

CN=colors.HexColor("#1A3A5C"); CB=colors.HexColor("#2563A8"); CB2=colors.HexColor("#5B9FE0")
CPB=colors.HexColor("#EEF5FD"); CR=colors.HexColor("#B22222"); CR2=colors.HexColor("#E05555")
CPR=colors.HexColor("#FDF0F0"); CW=colors.white; COW=colors.HexColor("#F8FAFF")
CDK=colors.HexColor("#1C2B3A"); CGR=colors.HexColor("#607080"); CLG=colors.HexColor("#F0F4F8")
CMG=colors.HexColor("#C5CDD5"); CBB=colors.HexColor("#B8D4F0"); CRB=colors.HexColor("#F0C0C0")
MARGIN=15*mm; HDR_H=60*mm; FTR_H=14*mm; TOP_GAP=8*mm; BOT_GAP=6*mm


def _download_to_temp(url: str) -> str:
    """Download a Cloudinary URL to a local temp file, return the path."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    urllib.request.urlretrieve(url, tmp.name)
    tmp.close()
    return tmp.name


def grad(c,x,y,w,h,c1,c2,n=18):
    r1,g1,b1=c1.red,c1.green,c1.blue; r2,g2,b2=c2.red,c2.green,c2.blue; sh=h/n
    for i in range(n):
        t=i/n; c.setFillColorRGB(r1+(r2-r1)*t,g1+(g2-g1)*t,b1+(b2-b1)*t)
        c.rect(x,y+h-sh*(i+1),w,sh+0.4,fill=1,stroke=0)

def hdr(c,W,H,CW_):
    grad(c,0,H-HDR_H,W,HDR_H,CN,colors.HexColor("#2E6BB5"))
    c.setFillColor(CR); c.rect(0,H-HDR_H-1.5*mm,W,1.5*mm,fill=1,stroke=0)
    c.setFillColor(CW); c.rect(0,H-HDR_H-2.5*mm,W,1*mm,fill=1,stroke=0)
    c.setFillColor(CW); c.roundRect(MARGIN,H-HDR_H+8*mm,26*mm,30*mm,3*mm,fill=1,stroke=0)
    c.setFillColor(CR2); c.rect(26*mm-1.5*mm,H-HDR_H+13*mm,3*mm,12*mm,fill=1,stroke=0)
    c.rect(20.5*mm,H-HDR_H+18*mm,11*mm,3*mm,fill=1,stroke=0)
    c.setFillColor(CB); c.setFont("Helvetica-Bold",6); c.drawCentredString(26*mm,H-HDR_H+9.5*mm,"BloodEye")
    c.setFillColor(CW); c.setFont("Helvetica-Bold",23); c.drawString(46*mm,H-20*mm,"BloodEye")
    grad(c,46*mm,H-23.5*mm,48*mm,1.5*mm,CR2,colors.HexColor("#E07070"))
    c.setFillColor(colors.HexColor("#A8C8F0")); c.setFont("Helvetica-Bold",9)
    c.drawString(46*mm,H-30*mm,"AI-Powered Ocular Blood Group Prediction System")
    c.setFillColor(colors.HexColor("#7AAED8")); c.setFont("Helvetica",8)
    c.drawString(46*mm,H-38*mm,"Confidential Medical Report  |  For Clinical Reference Only")
    now=datetime.now().strftime("%d %b %Y   %H:%M")
    grad(c,W-62*mm,H-19*mm,46*mm,10*mm,colors.HexColor("#0D2B55"),colors.HexColor("#1E5FAA"))
    c.setStrokeColor(colors.HexColor("#7AAED8")); c.setLineWidth(0.5)
    c.roundRect(W-62*mm,H-19*mm,46*mm,10*mm,2*mm,fill=0,stroke=1)
    c.setFillColor(CW); c.setFont("Helvetica-Bold",8); c.drawCentredString(W-39*mm,H-14.5*mm,now)
    grad(c,W-62*mm,H-34*mm,46*mm,9*mm,CR,CR2)
    c.setFillColor(CW); c.setFont("Helvetica-Bold",7.5); c.drawCentredString(W-39*mm,H-30.5*mm,"BLOOD GROUP REPORT")

def ftr(c,W,pg,total):
    grad(c,0,0,W,FTR_H,colors.HexColor("#EEF5FD"),colors.HexColor("#D6E8FA"))
    c.setStrokeColor(CBB); c.setLineWidth(0.7); c.line(0,FTR_H,W,FTR_H)
    c.setFillColor(CR2); c.rect(0,FTR_H-1*mm,W,1*mm,fill=1,stroke=0)
    c.setFillColor(CGR); c.setFont("Helvetica",7.5)
    c.drawString(MARGIN,5*mm,"BloodEye AI System  •  Confidential  •  Not a substitute for certified laboratory diagnosis")
    c.setFillColor(CB); c.setFont("Helvetica-Bold",8); c.drawRightString(W-MARGIN,5*mm,f"Page {pg} / {total}")

def sbar(c,y,title,CW_,blue=True):
    if blue: grad(c,MARGIN,y,CW_,7.5*mm,CB,CB2)
    else:    grad(c,MARGIN,y,CW_,7.5*mm,CR,CR2)
    c.setFillColor(CW); c.setFont("Helvetica-Bold",9.5); c.drawString(MARGIN+5*mm,y+2*mm,title.upper())

def icard(c,x,y,lbl,val,w=86*mm,h=15*mm,blue=True):
    a1=CB if blue else CR; a2=CB2 if blue else CR2; bd=CBB if blue else CRB
    c.setFillColor(CMG); c.roundRect(x+0.7*mm,y-0.7*mm,w,h,3*mm,fill=1,stroke=0)
    c.setFillColor(CW); c.roundRect(x,y,w,h,3*mm,fill=1,stroke=0)
    grad(c,x,y,3.5*mm,h,a1,a2)
    c.setFillColor(CGR); c.setFont("Helvetica",7); c.drawString(x+6*mm,y+h-4.5*mm,lbl.upper())
    c.setFillColor(CDK); c.setFont("Helvetica-Bold",10.5); c.drawString(x+6*mm,y+2.5*mm,str(val))
    c.setStrokeColor(bd); c.setLineWidth(0.6); c.roundRect(x,y,w,h,3*mm,fill=0,stroke=1)

def bdg(c,x,y,lbl,val,w=57*mm,h=27*mm,blue=False):
    c1=CN if blue else CR; c2=CB2 if blue else CR2
    c.setFillColor(CMG); c.roundRect(x+1*mm,y-1*mm,w,h,5*mm,fill=1,stroke=0)
    grad(c,x,y,w,h,c1,c2)
    c.setStrokeColor(CW); c.setLineWidth(1); c.roundRect(x,y,w,h,5*mm,fill=0,stroke=1)
    lc=colors.HexColor("#CCDFEF") if blue else colors.HexColor("#F5CECE")
    c.setFillColor(lc); c.setFont("Helvetica-Bold",7); c.drawCentredString(x+w/2,y+h-6.5*mm,lbl)
    c.setStrokeColor(CW); c.setLineWidth(0.3); c.line(x+7*mm,y+h-9*mm,x+w-7*mm,y+h-9*mm)
    c.setFillColor(CW); c.setFont("Helvetica-Bold",21); c.drawCentredString(x+w/2,y+5*mm,str(val))

def pbar(c,x,y,lbl,val,bw=108*mm,top=False):
    bh=7*mm; fw=bw*min(val/100,1)
    c.setFillColor(CLG); c.roundRect(x+16*mm,y,bw,bh,3*mm,fill=1,stroke=0)
    if fw>1*mm:
        if top: grad(c,x+16*mm,y,fw,bh,CR,CR2)
        else:   grad(c,x+16*mm,y,fw,bh,CB,CB2)
    c.setFillColor(CR if top else CDK); c.setFont("Helvetica-Bold" if top else "Helvetica",8.5)
    c.drawString(x,y+2*mm,lbl)
    c.setFillColor(CDK); c.setFont("Helvetica-Bold",8); c.drawRightString(x+16*mm+bw+12*mm,y+2*mm,f"{val:.1f}%")
    if top: c.setFillColor(CR2); c.setFont("Helvetica-Bold",8); c.drawString(x+16*mm+bw+13*mm,y+2*mm,"★")

def ftbl(c,x,y,data,tw=87*mm,blue=True):
    a1=CB if blue else CR; a2=CB2 if blue else CR2; bd=CBB if blue else CRB; bg=CPB if blue else CPR
    rh=8*mm; rows=list(data.items()); th=rh*(len(rows)+1)
    c.setFillColor(CMG); c.roundRect(x+0.7*mm,y-0.7*mm,tw,th,3*mm,fill=1,stroke=0)
    grad(c,x,y+th-rh,tw,rh,a1,a2)
    c.setFillColor(CW); c.setFont("Helvetica-Bold",8.5)
    c.drawString(x+4*mm,y+th-rh+2.5*mm,"Feature"); c.drawString(x+tw-22*mm,y+th-rh+2.5*mm,"Value")
    for i,(k,v) in enumerate(rows):
        ry=y+th-rh*(i+2); c.setFillColor(bg if i%2==0 else CW); c.rect(x,ry,tw,rh,fill=1,stroke=0)
        c.setFillColor(CDK); c.setFont("Helvetica",8); c.drawString(x+4*mm,ry+2.3*mm,str(k))
        c.setFillColor(a1); c.setFont("Helvetica-Bold",8.5); c.drawRightString(x+tw-4*mm,ry+2.3*mm,f"{round(float(v),4)}")
    c.setStrokeColor(bd); c.setLineWidth(0.8); c.roundRect(x,y,tw,th,3*mm,fill=0,stroke=1)
    return th


def download_report(request):
    fundus_tmp = None
    sclera_tmp = None

    try:
        from .ml.preprocess import preprocess_image
        from .ml.feature_extraction import extract_fundus_features, extract_sclera_features
        from .ml.predict import predict_blood_group

        # ── STEP 1: Get Cloudinary URLs from session ──────────────────────
        fundus_url = request.session.get("fundus_url")
        sclera_url = request.session.get("sclera_url")

        if not fundus_url or not sclera_url:
            return HttpResponse(
                "Images not found. Please re-upload and extract features first.",
                status=400
            )

        # ── STEP 2: Download fresh from Cloudinary → temp files ───────────
        import urllib.request, tempfile

        def fetch(url):
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            urllib.request.urlretrieve(url, tmp.name)
            tmp.close()
            return tmp.name

        fundus_tmp = fetch(fundus_url)
        sclera_tmp = fetch(sclera_url)
        fp = fundus_tmp
        sp = sclera_tmp

        # ── STEP 3: ML pipeline ────────────────────────────────────────────
        result   = predict_blood_group(fp, sp)
        ff       = extract_fundus_features(preprocess_image(fp))
        sf       = extract_sclera_features(preprocess_image(sp))
        user     = request.user.username
        email    = request.user.email
        pred_grp = result["predicted_group"]
        conf     = round(result["confidence"], 2)
        probs    = result["all_probabilities"]

        # ── STEP 4: Build PDF ──────────────────────────────────────────────
        from reportlab.lib.utils import ImageReader

        buf = BytesIO(); W,H = A4; CW_ = W-2*MARGIN
        CTOP = H-HDR_H-2.5*mm-TOP_GAP; G = 5*mm; TOTAL = 3
        c = canvas.Canvas(buf, pagesize=A4)

        # PAGE 1 ─────────────────────────────────────────────────────────
        hdr(c,W,H,CW_); ftr(c,W,1,TOTAL); y=CTOP
        sbar(c,y,"Patient Information",CW_); y-=7.5*mm+G
        icard(c,MARGIN,y,"Username",user,w=86*mm,blue=True)
        icard(c,MARGIN+93*mm,y,"Email Address",email,w=82*mm,blue=False)
        y-=15*mm+G+4*mm
        sbar(c,y,"Prediction Result",CW_,blue=False); y-=7.5*mm+G
        bdg(c,MARGIN,y,"PREDICTED BLOOD GROUP",pred_grp,w=57*mm,h=27*mm,blue=False)
        bdg(c,MARGIN+63*mm,y,"CONFIDENCE SCORE",f"{conf}%",w=57*mm,h=27*mm,blue=True)
        dx=MARGIN+128*mm
        c.setFillColor(CPR); c.roundRect(dx,y,47*mm,27*mm,3*mm,fill=1,stroke=0)
        c.setStrokeColor(CRB); c.setLineWidth(0.7); c.roundRect(dx,y,47*mm,27*mm,3*mm,fill=0,stroke=1)
        grad(c,dx,y+19*mm,47*mm,8*mm,CR,CR2); c.rect(dx,y+19*mm,47*mm,4*mm,fill=1,stroke=0)
        c.setFillColor(CW); c.setFont("Helvetica-Bold",7.5); c.drawCentredString(dx+23.5*mm,y+23*mm,"DISCLAIMER")
        c.setFillColor(CDK); c.setFont("Helvetica",7)
        for i,ln in enumerate(["AI prediction via ocular","analysis only. Please",
                                "confirm with a certified","laboratory blood test."]):
            c.drawString(dx+4*mm,y+16*mm-i*4.5*mm,ln)
        y-=27*mm+G+4*mm
        sbar(c,y,"Blood Group Probability Breakdown",CW_); y-=7.5*mm+G
        for rank,(lbl,val) in enumerate(sorted(probs.items(),key=lambda x:x[1],reverse=True)):
            pbar(c,MARGIN,y-7*mm,lbl,val,top=(rank==0)); y-=10*mm

        # PAGE 2 ─────────────────────────────────────────────────────────
        c.showPage(); hdr(c,W,H,CW_); ftr(c,W,2,TOTAL); y=CTOP
        sbar(c,y,"Extracted Ocular Features",CW_); y-=7.5*mm+G
        c.setFillColor(CB); c.setFont("Helvetica-Bold",8.5); c.drawString(MARGIN,y,"Fundus (Retinal) Features")
        c.setFillColor(CR); c.drawString(MARGIN+95*mm,y,"Sclera (Eye White) Features")
        y-=4*mm
        ftbl(c,MARGIN,y-68*mm,ff,tw=87*mm,blue=True)
        ftbl(c,MARGIN+93*mm,y-32*mm,sf,tw=87*mm,blue=False)
        y-=76*mm+G+3*mm
        c.setStrokeColor(CBB); c.setLineWidth(0.4); c.line(MARGIN,y+3*mm,W-MARGIN,y+3*mm)
        y-=4*mm
        sbar(c,y,"What These Features Mean",CW_); y-=7.5*mm+3*mm
        notes=[
            (True,"cnn_pca1","Deep CNN feature — captures retinal texture patterns."),
            (False,"AVR","Artery-to-vein ratio. Normal 0.6–0.75; lower may indicate hypertension."),
            (True,"vessel_red","Retinal vessel redness. Correlates with hemoglobin levels."),
            (False,"tortuosity","Vessel curvature. Higher values suggest vascular stress."),
            (True,"vessel_den","Vessel density. Linked to microcirculation health."),
            (False,"perivascular","Perivascular intensity. Elevated may flag inflammation."),
            (True,"pulse_std","Pulse std dev. Captures micro-pulsation patterns."),
            (False,"sclera_mean","Avg scleral brightness — baseline for eye-white colour analysis."),
            (True,"sclera_red","Scleral redness. Elevated may indicate anemia or jaundice."),
            (False,"AV_sat_diff","Artery-vein O2 saturation difference. Core oxygenation metric."),
        ]
        rh=9*mm
        for i,(ib,feat,desc) in enumerate(notes):
            ry=y-rh*(i+1)
            c.setFillColor(CPB if i%2==0 else COW); c.rect(MARGIN,ry,CW_,rh,fill=1,stroke=0)
            grad(c,MARGIN,ry,3.5*mm,rh,CB if ib else CR,CB2 if ib else CR2)
            c.setFillColor(CDK); c.setFont("Helvetica-Bold",8); c.drawString(MARGIN+6*mm,ry+2.8*mm,feat)
            c.setFillColor(CGR); c.setFont("Helvetica",8); c.drawString(MARGIN+50*mm,ry+2.8*mm,desc)
        c.setStrokeColor(CBB); c.setLineWidth(0.6)
        c.rect(MARGIN,y-rh*len(notes),CW_,rh*len(notes),fill=0,stroke=1)

        # PAGE 3 ─────────────────────────────────────────────────────────
        c.showPage(); hdr(c,W,H,CW_); ftr(c,W,3,TOTAL); y=CTOP
        sbar(c,y,"Clinical Eye Images",CW_); y-=7.5*mm+G

        IW=86*mm; IH=82*mm

        # ✅ Draw BOTH image cards in the loop — NO try/except/else
        for ix,(lbl,img_path,ib) in enumerate([
            ("Fundus (Retinal) Image",   fp, True),
            ("Sclera (Eye White) Image", sp, False),
        ]):
            px = MARGIN + ix*(IW+8*mm)
            a1=CB if ib else CR; a2=CB2 if ib else CR2
            bd=CBB if ib else CRB; bg=CPB if ib else CPR

            # Card background
            c.setFillColor(bg)
            c.roundRect(px, y-IH, IW, IH, 4*mm, fill=1, stroke=0)

            # Title bar
            grad(c, px, y-10*mm, IW, 9*mm, a1, a2)
            c.setFillColor(CW); c.setFont("Helvetica-Bold", 9)
            c.drawCentredString(px+IW/2, y-6.5*mm, lbl)

            # ✅ Draw image — ImageReader handles local file path correctly
            image_drawn = False
            if img_path and os.path.exists(img_path):
                try:
                    c.drawImage(
                        ImageReader(img_path),
                        px+4*mm, y-IH+4*mm,
                        width=IW-8*mm, height=IH-16*mm,
                        preserveAspectRatio=True, anchor='c'
                    )
                    image_drawn = True
                except Exception as draw_err:
                    print(f"[BloodEye] drawImage error: {draw_err}")

            # ✅ Placeholder ONLY if image failed — NOT in else of try
            if not image_drawn:
                c.setFillColor(CLG)
                c.roundRect(px+4*mm, y-IH+4*mm, IW-8*mm, IH-16*mm, 3*mm, fill=1, stroke=0)
                c.setFillColor(CMG); c.setFont("Helvetica",8)
                c.drawCentredString(px+IW/2, y-IH/2, "[ Image unavailable ]")

            # Card border
            c.setStrokeColor(bd); c.setLineWidth(1)
            c.roundRect(px, y-IH, IW, IH, 4*mm, fill=0, stroke=1)

        # ✅ y advances ONCE after the loop — not inside it
        y -= IH+G+4*mm

        # About block
        about_h=34*mm
        c.setFillColor(CPB); c.roundRect(MARGIN,y-about_h,CW_,about_h,3*mm,fill=1,stroke=0)
        c.setStrokeColor(CBB); c.setLineWidth(0.6); c.roundRect(MARGIN,y-about_h,CW_,about_h,3*mm,fill=0,stroke=1)
        grad(c,MARGIN,y-9*mm,CW_,8*mm,CB,CB2)
        c.setFillColor(CW); c.setFont("Helvetica-Bold",8.5); c.drawString(MARGIN+5*mm,y-6*mm,"About the Clinical Images")
        c.setFillColor(CDK); c.setFont("Helvetica",8)
        for i,ln in enumerate([
            "Fundus Image: Retinal photograph for vessel feature extraction (AVR, redness,",
            "tortuosity, density) — correlating with blood composition and circulatory patterns.","",
            "Sclera Image: Eye-white photograph to measure scleral redness and colour saturation,",
            "reflecting conditions like anemia, jaundice, or blood oxygenation changes.",
        ]):
            c.drawString(MARGIN+5*mm,y-13*mm-i*4.5*mm,ln)
        y-=about_h+G+3*mm

        # Summary banner
        sum_h=17*mm
        grad(c,MARGIN,y-sum_h,CW_,sum_h,CN,colors.HexColor("#2E6BB5"))
        c.setStrokeColor(CB2); c.setLineWidth(0.5); c.roundRect(MARGIN,y-sum_h,CW_,sum_h,2*mm,fill=0,stroke=1)
        c.setFillColor(CW); c.setFont("Helvetica-Bold",9.5)
        c.drawString(MARGIN+8*mm,y-7.5*mm,"BloodEye AI System — Prediction Summary")
        c.setFillColor(colors.HexColor("#A8C8F0")); c.setFont("Helvetica",8.5)
        c.drawString(MARGIN+8*mm,y-14*mm,
            f"Patient: {user}   |   Predicted Group: {pred_grp}   |   "
            f"Confidence: {conf}%   |   {datetime.now().strftime('%d %b %Y')}")

        c.save(); buf.seek(0)
        response = HttpResponse(buf.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="BloodEye_Report.pdf"'
        return response

    except Exception as e:
        import traceback; traceback.print_exc()
        return HttpResponse(f"Error: {str(e)}", status=500)

    finally:
        # Always delete temp files
        for tmp in (fundus_tmp, sclera_tmp):
            if tmp and os.path.exists(tmp):
                try: os.unlink(tmp)
                except: pass