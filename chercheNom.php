<?php
include_once("commun.php");

header('Content-Type: application/json');

$sql =  "SELECT surname FROM person where surname like '%".$_GET["term"]."%'";
$data=[];
foreach  ($pdo->query($sql) as $row) {
    if (!in_array($row["surname"],$data)){
        array_push($data,$row["surname"]);
    }
}
sort($data);
echo json_encode($data);

?>
