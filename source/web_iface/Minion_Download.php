<html>

<!DOCTYPE html>
<html>
<head>
<title>Download Data XXX</title>
<style>
    h1 {text-align: center;}
    body {
        width: 35em;
        margin: 0 auto;
        font-family: Tahoma, Verdana, Arial, sans-serif;
        /*background-color:lightskyblue;*/
    }
.testDiv {
    border: 5px outset red;
}
</style>
    <meta charset="UTF-8">
    <script type="text/javascript" src="autoUpdate.js"></script>
</head>

<body>

<h1>Download Minion XXX Data</h1>

<br>
<br>
<p1>First Zip data to file:</p1>
<br>
<br>
<button type="button" onclick="window.open('#','_blank');window.open('zipfiles.php','_self');">Zip Data Files</button>
<br>
<br>
<p1>Second Download data:</p1>
<br>
<br>
<form method='post' action=''>
<input type='submit' name='download' value='Download Data' />
</form>
<br>

<?php
if(isset($_POST['download'])){

$zip_file = 'MinionXXX.zip';

header('Content-Description: File Transfer');
header('Content-Type: application/octet-stream');
header('Content-Disposition: attachment; filename='.basename($zip_file));
header('Content-Transfer-Encoding: binary');
header('Expires: 0');
header('Cache-Control: must-revalidate');
header('Pragma: public');
header('Content-Length: ' . filesize("/var/www/html/".$zip_file));
ob_end_clean();
ob_clean();
flush();
readfile($zip_file);

}
?>

<div id="liveData">
    <p>Loading Data...</p>
</div>

<form action="/index.php" method="post">
<input type="submit" value="Return">
</form>

</body>
</html>
