<?php
header('Content-Type: application/json');
try{
    $pdo = new PDO('sqlite:'.dirname(__FILE__).'/db/names.db');
    $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION); // ERRMODE_WARNING | ERRMODE_EXCEPTION | ERRMODE_SILENT
} catch(Exception $e) {
    echo "Impossible d'accéder à la base de données SQLite : ".$e->getMessage();
    die();
}
$sql =  "SELECT surname FROM person where surname like '%".$_GET["term"]."%'";
$data=[];
foreach  ($pdo->query($sql) as $row) {
    array_push($data,$row["surname"]);
}
echo json_encode($data);

?>
