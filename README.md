# CNC File Translator
_Utility used to convert .nc files from PenguinCAM to .sbp files to use for ShopBot MAX CNC_


**1. GET SKETCH INTO PENGUINCAM**
  * Create CAD file in [OnShape](https://cad.onshape.com/)
  * Make sure [PenguinCAM](https://github.com/6238/PenguinCAM) is installed
  * Click on PenguinCAM icon in bottom-right corner of OnShape PartStudio
  * Select face of part that you want to CNC out
  * Choose to open in PenguinCAM
    
**2. GET .NC FILE FROM PENGUINCAM**
  * Choose desired settings for cutting out part
  * Generate GCode file as ```.nc```
    
**3. CONVERT TO .SBP FILE**
  * Go to online [GCode Translator app](https://etech-shopbot.streamlit.app/)
  * Upload ```.nc``` file
  * Download ```.sbp``` file
    
**4. RUN .SBP FILE ON SHOPBOT**
  * Open [Shopbot SB3 Control Software](https://shopbottools.com/support-resources/control-software/) on Windows computer
  * Run Shopbot CNC machine to cut part
