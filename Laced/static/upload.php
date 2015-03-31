<?php
$error = '';
	if($error == ''){
		$userCheck = '';
		$username = $_POST['username'];
        //Database connection
		$conn = new PDO('mysql:host=localhost;dbname=ssllab3;port=8889', 'root', 'root');
		$sql = 'SELECT username, password, thumb, image FROM users where username = "'.$username.'";';
		foreach ($conn->query($sql) as $row){
            $userCheck = $row['username'];
        }
		if($userCheck==$_POST['username']){
            $error='That username already exits';
        }
	}

	if($error == ''){
		//salt and hasing
		$salt = $_POST['username'];
		$password = $_POST['password'];

		//user info input
		$username = $_POST['username'];
		$password = md5($salt.$password);
		$thumb = "uploads/thumb_".$_FILES['userfile']['name'];
		$img = "uploads/".$_FILES['userfile']['name'];

		//mysql calls
		$stmt = $conn->prepare("insert into users (username, password,image,thumb) values(:username,:password,:img,:thumb);");
		$stmt->bindParam(':username',$username);
		$stmt->bindParam(':password',$password);
		$stmt->bindParam(':thumb',$thumb);
		$stmt->bindParam(':img',$img);
		$stmt->execute();
        
    //Resize Image Function
    function imageResize($file, $name, $h, $w){
    $type=substr($file, -3);
	switch($type){
		case $type == 'jpg':
			$canvas = imagecreatefromjpeg($file);
			break;
		case $type == 'png':
			$canvas = imagecreatefrompng($file);
			break;
	}
	$size = getimagesize($file);
	$fileWidth = $size[0];
	$fileHeight = $size[1];
	$content = imagecreatetruecolor($w, $h);
	imagecopyresampled($content,$canvas,0,0,0,0,$w,$h,$fileWidth,$fileHeight);
	imagepng($content,$name,9);
	imagedestroy($canvas);
}
           
	//set up image directory
    $uploaddir = "./uploads/";
	$uploadfile = $uploaddir . basename($_FILES["userfile"]["name"]);
        //Call image resize function
		if(move_uploaded_file($_FILES['userfile']['tmp_name'], $uploadfile)){
			imageResize("uploads/".$_FILES['userfile']['name'], 'uploads/thumb_'.$_FILES['userfile']['name'],100,100);
		}
	}

if($error == ''){
	foreach ($conn->query($sql) as $row){
		$username = $row['username'];
		$password = $row['password'];
		$img = $row['image'];
		$thumb = $row['thumb'];
	}

	echo "<!DOCTYPE html>
<html>
<head>
<title>Profile</title>
<style>html body{background: #fff;}img{background: #000000; padding: 3px;}</style>

</head>
<html>
	<center>
		<img class='thumb' src='".$thumb."' /><br />
		<h3>Username: ".$username."</h3>
		<p>Password Key:".$password."</p><br />	
	</center>
</html>";
}else{
	echo "<span>$error</span>";
	include "index.php";
}
?>