<?php
header('Content-Type: application/json');
$db = new SQLite3('names.db');
$results = $db->query("SELECT surname FROM person where surname like '%".$_GET["term"]."%'");
$data=[];
while ($row = $results->fetchArray()) {
    array_push($data,$row[0]);
}
echo json_encode($data);

?>
