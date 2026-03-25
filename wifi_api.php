<?php
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');

$pythonCmd = 'python';

if (strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
    $pythonCmd = 'python';
} else {
    $pythonCmd = 'python3';
}

$scriptPath = __DIR__ . '/wifi_scanner.py';

if (!file_exists($scriptPath)) {
    echo json_encode([
        'error' => 'Python script not found',
        'path' => $scriptPath
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

$descriptorspec = [
    0 => ["pipe", "r"],
    1 => ["pipe", "w"],
    2 => ["pipe", "w"]
];

$process = proc_open(
    $pythonCmd . ' "' . $scriptPath . '"',
    $descriptorspec,
    $pipes,
    null,
    null,
    ['bypass_shell' => true]
);

if (is_resource($process)) {
    $output = stream_get_contents($pipes[1]);
    $error = stream_get_contents($pipes[2]);
    
    fclose($pipes[0]);
    fclose($pipes[1]);
    fclose($pipes[2]);
    
    proc_close($process);
    
    if ($output) {
        $result = json_decode($output, true);
        if ($result) {
            echo json_encode($result, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
        } else {
            echo json_encode([
                'error' => 'Failed to parse Python output',
                'raw' => $output
            ], JSON_UNESCAPED_UNICODE);
        }
    } else {
        echo json_encode([
            'error' => 'No output from Python script',
            'stderr' => $error
        ], JSON_UNESCAPED_UNICODE);
    }
} else {
    echo json_encode([
        'error' => 'Failed to execute Python script'
    ], JSON_UNESCAPED_UNICODE);
}
