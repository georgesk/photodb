<?php
include_once("commun.php");

header('Content-Type: application/json');

$sql =  "SELECT surname FROM person where surname like '%".$_GET["term"]."%'";
$data=[];
foreach  ($pdo->query($sql) as $row) {
    array_push($data,$row["surname"]);
}
echo json_encode($data);

?>
