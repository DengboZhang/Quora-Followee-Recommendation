<html>

<head>

<?php
if (isset($_POST['Hello'])) {
	$keyword = $_POST['keyword'];

	$execpath = "python /opt/lampp/htdocs/mytest/hello.py ".$keyword;
	echo exec($execpath);
}
if (isset($_POST['Bye'])) {
	echo exec("python /opt/lampp/htdocs/mytest/bye.py");
}
?>

<form method="post" action="test.php">
	<input id="keyword" name="keyword" type="text"></input>
	<button class="btn" name="Hello">Hello</button> 
	<button class="btn" name="Bye">Bye</button>
</form>
</html>