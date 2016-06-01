
# contains three HTML snippets for constructing account


# table_html is the repetetive html that goes into the Fees Table
table_html = '''<tr><td>%s</td><td>$</td><td style="text-align:right"> %.2f</td>
                    </tr>\n'''

# base_html is the top half of the account
# the attribute in the <html> tag stops Firefox
# from printing out the address of the page - Firefox specific
base_html = '''<html moznomarginboxes mozdisallowselectionprint>
<head>
<style>
th {text-align: left;}
</style>
</head>
<body>
<h2 style="text-align:center">Account for Anaesthetic</h2><br>
<h3>Dr John Tillett</h3>
7 Henry Lawson Drive<br>
Villawood NSW 2163<br>
<br>
Provider Number: 0307195H<br>
<br>
Account Enquiries: ph 0408 116 320 fax 02 8382 6602<br>
<br>
<em>Patient Details:</em><br>
<br>
<strong>%s</strong><br>
%s<br>
%s<br>
<br>
<strong>%s</strong><br>
<br>
%s<br>
<br>
Date of Procedure: %s<br>
<br>
Place of Procedure: Diagnostic Endoscopy Centre, Darlinghurst, NSW 2010<br>
<br>
Procedure performed by Dr. %s<br>
<br><br>
<table>
<tr>
<th style="width:250px">Item Number</th>
<th></th>
<th>Fee</th>
</tr>
<tr><td>17610</td><td>$</td><td style="text-align:right">%.2f</td></tr>'''

# terminal_html is appended on bottom of html code
terminal_html = '</table>\n</body>\n</html>'
