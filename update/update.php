<?php

$file_name = 'domain.json';

$domain = file_get_contents($file_name);
$domain_arr = json_decode($domain, true);

$data = $_POST['domain'] ?? '';

if (strlen($data) === $domain_arr['length'] || $data === '-') {
    $domain_arr['start'] = $data;
    
    file_put_contents($file_name, json_encode($domain_arr));
}

echo json_encode($domain_arr);
