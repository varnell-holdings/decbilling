The purpose of decbilling is to:

1. Generate a web page to tell the DEC secretaries what was done in the procedure room - docbill_start.py
2. Help secretarial staff automatically fill that data into the day surgery module - watcher.py
3. Collect data for anaesthetists who use Meditrust billing service - meditrust_writer function inside docbill_start.py
4. Print anaesthetic accounts - decbatches.py
5. Provide a simple analysis package to tell jrt how many patients he needs to do to reach a target - jt_target.py
6. Automate patient data entry into Endobase program by typists and import that data into docbill - endobase.py (separate module in github)
7. Collect data for QPS and provide programs to present that data - caecum.py & repeat_procedures.py
8. Generate emails to patients for quality control.
