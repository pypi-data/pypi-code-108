DEFAULT_HTML = '''
<!DOCTYPE html>
<html lang="en">
<div>
    <h2 style="text-align: center;"><span style="color: #F76723;"><strong>Welcome to cloudshell-email</strong></span></h2>
</div>
<div>
    <p><span style="color: #000000;">This is the default html template using the cloudshell-email package.</span></p>
</div>
<div>
    <p><span style="color: #000000;">The cloudshell-email package can be used to send emails to users from orchestration scripts.</span></p>
</div>
<div>
    <p><span style="color: #000000;"><strong>You can view cloudshell-email usage guide here:</strong></span></p>
</div>
<div>
    <span style="color: #000000;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
        <a href="https://github.com/QualiSystemsLab/cloudshell-email"> Github Repo </a>
    </span>
</div>
</body>
</html>
'''
VALID_EMAIL_REGEX = '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'