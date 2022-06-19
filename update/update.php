<?php

$domain = file_get_contents('domain.json');
$domain_arr = json_decode($domain, true);

$data = $_POST['domain'] ?? '';

if (strlen($data) === $domain_arr['length']) {
    $domain_arr['start'] = $data;
}

echo json_encode($domain_arr);