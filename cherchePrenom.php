<?php
header('Content-Type: application/json');
$db = new SQLite3('db/names.db');
$nom=$_GET["nom"];
$term=$_GET["prenom"];
$results = $db->query("SELECT givenname FROM person where surname = '".$nom."' and givenname like '%".$term."%'");
$data=[];
while ($row = $results->fetchArray()) {
    array_push($data,$row[0]);
}
echo json_encode($data);

?>
