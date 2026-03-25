import subprocess
import json
import platform
import re
import os
import socket
import urllib.request
import time
from flask import Flask, render_template_string, request, jsonify
from functools import wraps

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WiFi & Network Scanner</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&display=swap');
        
        * {
            font-family: 'Prompt', sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            color: #fff;
        }
        
        .glass-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        
        .stat-card {
            background: linear-gradient(145deg, rgba(255,255,255,0.15), rgba(255,255,255,0.05));
            border-radius: 16px;
            padding: 20px;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0, 150, 255, 0.3);
        }
        
        .stat-icon {
            font-size: 2.5rem;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #00d4ff, #7b2cbf);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .stat-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #00d4ff;
        }
        
        .stat-label {
            color: rgba(255,255,255,0.7);
            font-size: 0.9rem;
        }
        
        .speed-gauge {
            position: relative;
            width: 200px;
            height: 200px;
            margin: 0 auto;
        }
        
        .speed-gauge svg {
            transform: rotate(-90deg);
        }
        
        .speed-gauge circle {
            fill: none;
            stroke-width: 15;
        }
        
        .speed-gauge .bg {
            stroke: rgba(255,255,255,0.1);
        }
        
        .speed-gauge .progress {
            stroke: url(#gradient);
            stroke-linecap: round;
            transition: stroke-dashoffset 1s ease;
        }
        
        .speed-value {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 2.5rem;
            font-weight: 700;
        }
        
        .speed-unit {
            font-size: 1rem;
            color: rgba(255,255,255,0.6);
        }
        
        .btn-scan {
            background: linear-gradient(45deg, #00d4ff, #7b2cbf);
            border: none;
            padding: 15px 40px;
            font-size: 1.1rem;
            border-radius: 50px;
            color: white;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 5px 20px rgba(0, 212, 255, 0.4);
        }
        
        .btn-scan:hover {
            transform: scale(1.05);
            box-shadow: 0 8px 30px rgba(0, 212, 255, 0.6);
        }
        
        .btn-scan:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .isp-card {
            background: linear-gradient(145deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
            border-radius: 12px;
            padding: 15px 20px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        .isp-logo {
            width: 50px;
            height: 50px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            margin-right: 15px;
        }
        
        .isp-info h6 {
            margin: 0;
            font-weight: 600;
        }
        
        .isp-info p {
            margin: 0;
            font-size: 0.85rem;
            color: rgba(255,255,255,0.6);
        }
        
        .isp-link {
            padding: 8px 20px;
            border-radius: 20px;
            text-decoration: none;
            font-size: 0.85rem;
            transition: all 0.3s ease;
        }
        
        .chart-container {
            position: relative;
            height: 250px;
        }
        
        .pulse {
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .loading-spinner {
            width: 50px;
            height: 50px;
            border: 4px solid rgba(255,255,255,0.1);
            border-top-color: #00d4ff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
        }
        
        .status-online { background: #00ff88; box-shadow: 0 0 10px #00ff88; }
        .status-offline { background: #ff4757; box-shadow: 0 0 10px #ff4757; }
        
        header {
            background: rgba(0,0,0,0.3);
            padding: 20px 0;
            margin-bottom: 30px;
        }
        
        .wifi-card {
            transition: all 0.3s ease;
        }
        
        .wifi-card:hover {
            transform: translateY(-3px);
            background: rgba(255, 255, 255, 0.15);
        }
        
        .btn-scan.btn-sm {
            padding: 8px 20px;
            font-size: 0.9rem;
            border-radius: 25px;
        }
        
        .text-purple {
            color: #8b5cf6 !important;
        }
        
        .form-control, .form-select {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: #fff;
        }
        
        .form-control:focus, .form-select:focus {
            background: rgba(255, 255, 255, 0.15);
            border-color: #00d4ff;
            color: #fff;
            box-shadow: 0 0 0 0.2rem rgba(0, 212, 255, 0.25);
        }
        
        .form-control::placeholder {
            color: rgba(255, 255, 255, 0.5);
        }
        
        .form-select option {
            background: #1a1a2e;
            color: #fff;
        }
        
        .form-check-input {
            background-color: rgba(255, 255, 255, 0.1);
            border-color: rgba(255, 255, 255, 0.3);
        }
        
        .form-check-input:checked {
            background-color: #00d4ff;
            border-color: #00d4ff;
        }
        
        .btn-outline-secondary {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: #fff;
        }
        
        .btn-outline-secondary:hover {
            background: rgba(255, 255, 255, 0.2);
            border-color: rgba(255, 255, 255, 0.3);
            color: #fff;
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <div class="d-flex justify-content-between align-items-center">
                <div class="d-flex align-items-center">
                    <i class="fas fa-wifi fa-2x me-3" style="color: #00d4ff;"></i>
                    <div>
                        <h4 class="mb-0">WiFi & Network Scanner</h4>
                        <small class="text-muted">ตรวจสอบคุณภาพอินเทอร์เน็ตของคุณ</small>
                    </div>
                </div>
                <div class="d-flex align-items-center">
                    <span class="status-indicator status-online" id="connectionStatus"></span>
                    <span id="connectionText">เชื่อมต่อแล้ว</span>
                </div>
            </div>
        </div>
    </header>

    <div class="container pb-5">
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="stat-card glass-card">
                    <i class="fas fa-globe stat-icon"></i>
                    <div class="stat-value" id="ipAddress">...</div>
                    <div class="stat-label">IP Address</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card glass-card">
                    <i class="fas fa-building stat-icon"></i>
                    <div class="stat-value" id="ispName">...</div>
                    <div class="stat-label">ผู้ให้บริการ (ISP)</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card glass-card">
                    <i class="fas fa-map-marker-alt stat-icon"></i>
                    <div class="stat-value" id="location">...</div>
                    <div class="stat-label">ตำแหน่ง</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card glass-card">
                    <i class="fas fa-signal stat-icon"></i>
                    <div class="stat-value" id="networkType">...</div>
                    <div class="stat-label">ประเภท Network</div>
                </div>
            </div>
        </div>

        <div class="row mb-4">
            <div class="col-lg-6 mb-4">
                <div class="glass-card p-4">
                    <h5 class="mb-4"><i class="fas fa-tachometer-alt me-2"></i>ทดสอบความเร็วอินเทอร์เน็ต</h5>
                    <div class="speed-gauge mb-4">
                        <svg width="200" height="200">
                            <defs>
                                <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                                    <stop offset="0%" style="stop-color:#00d4ff"/>
                                    <stop offset="100%" style="stop-color:#7b2cbf"/>
                                </linearGradient>
                            </defs>
                            <circle class="bg" cx="100" cy="100" r="85"/>
                            <circle class="progress" id="speedCircle" cx="100" cy="100" r="85" 
                                stroke-dasharray="534" stroke-dashoffset="534"/>
                        </svg>
                        <div class="speed-value">
                            <span id="speedValue">0</span>
                            <span class="speed-unit">Mbps</span>
                        </div>
                    </div>
                    <div class="text-center">
                        <button class="btn-scan" id="startTest" onclick="startSpeedTest()">
                            <i class="fas fa-play me-2"></i>เริ่มทดสอบความเร็ว
                        </button>
                    </div>
                </div>
            </div>
            
            <div class="col-lg-6 mb-4">
                <div class="glass-card p-4">
                    <h5 class="mb-4"><i class="fas fa-chart-line me-2"></i>กราฟความเร็ว</h5>
                    <div class="chart-container">
                        <canvas id="speedChart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mb-4">
            <div class="col-12">
                <div class="glass-card p-4">
                    <div class="d-flex justify-content-between align-items-center mb-4">
                        <h5 class="mb-0"><i class="fas fa-wifi me-2"></i>WiFi Networks ที่พบ</h5>
                        <button class="btn-scan btn-sm" id="scanBtn" onclick="scanWifi()">
                            <i class="fas fa-sync-alt me-1"></i> Scan WiFi
                        </button>
                    </div>
                    <div id="wifiResults" class="row">
                        <div class="col-12 text-center py-4">
                            <div class="loading-spinner mx-auto mb-3" id="wifiLoading" style="display: none;"></div>
                            <p class="text-muted" id="wifiStatus">กดปุ่ม Scan WiFi เพื่อค้นหาเครือข่าย</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mb-4">
            <div class="col-md-6 mb-4">
                <div class="glass-card p-4">
                    <h5 class="mb-4"><i class="fas fa-signal me-2"></i>ความแรงสัญญาณ WiFi</h5>
                    <div class="chart-container" style="height: 200px;">
                        <canvas id="wifiSignalChart"></canvas>
                    </div>
                </div>
            </div>
            <div class="col-md-6 mb-4">
                <div class="glass-card p-4">
                    <h5 class="mb-4"><i class="fas fa-globe me-2"></i>ความเร็ว Internet</h5>
                    <div class="chart-container" style="height: 200px;">
                        <canvas id="internetSpeedChart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mb-4">
            <div class="col-12">
                <div class="glass-card p-4">
                    <h5 class="mb-4"><i class="fas fa-cog me-2"></i>การตั้งค่า WiFi</h5>
                    <form id="wifiConfigForm" onsubmit="connectToWifi(event)">
                        <div class="row">
                            <div class="col-md-4 mb-3">
                                <label class="form-label"><i class="fas fa-wifi me-2"></i>SSID (ชื่อ WiFi)</label>
                                <select class="form-select" id="wifiSSID" onchange="onSSIDChange()">
                                    <option value="">-- เลือก WiFi --</option>
                                </select>
                            </div>
                            <div class="col-md-4 mb-3">
                                <label class="form-label"><i class="fas fa-user me-2"></i>Username</label>
                                <input type="text" class="form-control" id="wifiUsername" placeholder="กรอก Username (ถ้ามี)">
                            </div>
                            <div class="col-md-4 mb-3">
                                <label class="form-label"><i class="fas fa-key me-2"></i>Password</label>
                                <div class="input-group">
                                    <input type="password" class="form-control" id="wifiPassword" placeholder="กรอก Password">
                                    <button class="btn btn-outline-secondary" type="button" onclick="togglePassword()">
                                        <i class="fas fa-eye" id="toggleIcon"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-4 mb-3">
                                <label class="form-label"><i class="fas fa-shield-alt me-2"></i>Security Type</label>
                                <select class="form-select" id="wifiSecurity">
                                    <option value="WPA">WPA/WPA2</option>
                                    <option value="WEP">WEP</option>
                                    <option value="Open">Open (ไม่มีรหัสผ่าน)</option>
                                </select>
                            </div>
                            <div class="col-md-4 mb-3">
                                <label class="form-label">&nbsp;</label>
                                <div class="form-check mt-2">
                                    <input class="form-check-input" type="checkbox" id="saveConfig">
                                    <label class="form-check-label" for="saveConfig">
                                        บันทึกการตั้งค่า
                                    </label>
                                </div>
                            </div>
                            <div class="col-md-4 mb-3 d-flex align-items-end">
                                <button type="submit" class="btn-scan w-100" id="connectBtn">
                                    <i class="fas fa-plug me-2"></i>เชื่อมต่อ WiFi
                                </button>
                            </div>
                        </div>
                    </form>
                    <div id="connectStatus" class="mt-3" style="display: none;"></div>
                </div>
            </div>
        </div>

        <div class="row mb-4">
            <div class="col-12">
                <div class="glass-card p-4">
                    <h5 class="mb-4"><i class="fas fa-tower-cell me-2"></i>ผู้ให้บริการอินเทอร์เน็ต (ISP) ในประเทศไทย</h5>
                    <div class="row" id="ispList">
                        <div class="col-md-6 mb-3">
                            <div class="isp-card">
                                <div class="d-flex align-items-center">
                                    <div class="isp-logo" style="background: linear-gradient(45deg, #ff6b35, #f7931e);">
                                        <i class="fas fa-bolt text-white"></i>
                                    </div>
                                    <div class="isp-info">
                                        <h6>TRUE Online</h6>
                                        <p>บริการอินเทอร์เน็ตความเร็วสูง</p>
                                    </div>
                                </div>
                                <a href="https://www.trueinternet.co.th/" target="_blank" class="isp-link" style="background: #ff6b35; color: white;">
                                    สมัคร<i class="fas fa-external-link-alt ms-1"></i>
                                </a>
                            </div>
                        </div>
                        <div class="col-md-6 mb-3">
                            <div class="isp-card">
                                <div class="d-flex align-items-center">
                                    <div class="isp-logo" style="background: linear-gradient(45deg, #00a8e8, #007ea7);">
                                        <i class="fas fa-home text-white"></i>
                                    </div>
                                    <div class="isp-info">
                                        <h6>3BB</h6>
                                        <p>อินเทอร์เน็ตไฟเบอร์ออปติก</p>
                                    </div>
                                </div>
                                <a href="https://www.3bb.co.th/" target="_blank" class="isp-link" style="background: #00a8e8; color: white;">
                                    สมัคร<i class="fas fa-external-link-alt ms-1"></i>
                                </a>
                            </div>
                        </div>
                        <div class="col-md-6 mb-3">
                            <div class="isp-card">
                                <div class="d-flex align-items-center">
                                    <div class="isp-logo" style="background: linear-gradient(45deg, #8b5cf6, #6366f1);">
                                        <i class="fas fa-satellite-dish text-white"></i>
                                    </div>
                                    <div class="isp-info">
                                        <h6> AIS Fibre</h6>
                                        <p>อินเทอร์เน็ตไฟเบอร์และ5G</p>
                                    </div>
                                </div>
                                <a href="https://www.ais.th/fibre" target="_blank" class="isp-link" style="background: #8b5cf6; color: white;">
                                    สมัคร<i class="fas fa-external-link-alt ms-1"></i>
                                </a>
                            </div>
                        </div>
                        <div class="col-md-6 mb-3">
                            <div class="isp-card">
                                <div class="d-flex align-items-center">
                                    <div class="isp-logo" style="background: linear-gradient(45deg, #ec4899, #be185d);">
                                        <i class="fas fa-mobile-alt text-white"></i>
                                    </div>
                                    <div class="isp-info">
                                        <h6>DTAC</h6>
                                        <p>อินเทอร์เน็ตมือถือและบรอดแบนด์</p>
                                    </div>
                                </div>
                                <a href="https://www.dtac.co.th/" target="_blank" class="isp-link" style="background: #ec4899; color: white;">
                                    สมัคร<i class="fas fa-external-link-alt ms-1"></i>
                                </a>
                            </div>
                        </div>
                        <div class="col-md-6 mb-3">
                            <div class="isp-card">
                                <div class="d-flex align-items-center">
                                    <div class="isp-logo" style="background: linear-gradient(45deg, #10b981, #059669);">
                                        <i class="fas fa-network-wired text-white"></i>
                                    </div>
                                    <div class="isp-info">
                                        <h6>CAT Telecom</h6>
                                        <p>บริการอินเทอร์เน็ตภาครัฐ</p>
                                    </div>
                                </div>
                                <a href="https://www.cattelecom.com/" target="_blank" class="isp-link" style="background: #10b981; color: white;">
                                    สมัคร<i class="fas fa-external-link-alt ms-1"></i>
                                </a>
                            </div>
                        </div>
                        <div class="col-md-6 mb-3">
                            <div class="isp-card">
                                <div class="d-flex align-items-center">
                                    <div class="isp-logo" style="background: linear-gradient(45deg, #f59e0b, #d97706);">
                                        <i class="fas fa-broadcast-tower text-white"></i>
                                    </div>
                                    <div class="isp-info">
                                        <h6>TOT</h6>
                                        <p>บริการอินเทอร์เน็ตภาครัฐ</p>
                                    </div>
                                </div>
                                <a href="https://www.tot.co.th/" target="_blank" class="isp-link" style="background: #f59e0b; color: white;">
                                    สมัคร<i class="fas fa-external-link-alt ms-1"></i>
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row">
            <div class="col-12">
                <div class="glass-card p-4">
                    <h5 class="mb-4"><i class="fas fa-info-circle me-2"></i>ข้อมูล Network โดยละเอียด</h5>
                    <div class="row">
                        <div class="col-md-6">
                            <table class="table table-dark table-borderless">
                                <tr>
                                    <td><i class="fas fa-server me-2 text-info"></i>Public IP</td>
                                    <td id="publicIp" class="text-end">...</td>
                                </tr>
                                <tr>
                                    <td><i class="fas fa-desktop me-2 text-info"></i>Local IP</td>
                                    <td id="localIp" class="text-end">...</td>
                                </tr>
                                <tr>
                                    <td><i class="fas fa-network-wired me-2 text-info"></i>MAC Address</td>
                                    <td id="macAddress" class="text-end">ไม่สามารถดึงได้</td>
                                </tr>
                                <tr>
                                    <td><i class="fas fa-window-maximize me-2 text-info"></i>Browser</td>
                                    <td id="browser" class="text-end">...</td>
                                </tr>
                            </table>
                        </div>
                        <div class="col-md-6">
                            <table class="table table-dark table-borderless">
                                <tr>
                                    <td><i class="fas fa-microchip me-2 text-purple"></i>Platform</td>
                                    <td id="platform" class="text-end">...</td>
                                </tr>
                                <tr>
                                    <td><i class="fas fa-language me-2 text-purple"></i>Language</td>
                                    <td id="language" class="text-end">...</td>
                                </tr>
                                <tr>
                                    <td><i class="fas fa-clock me-2 text-purple"></i>Timezone</td>
                                    <td id="timezone" class="text-end">...</td>
                                </tr>
                                <tr>
                                    <td><i class="fas fa-calendar me-2 text-purple"></i>วันที่</td>
                                    <td id="currentDate" class="text-end">...</td>
                                </tr>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <footer class="text-center py-4" style="color: rgba(255,255,255,0.5);">
        <small>WiFi & Network Scanner &copy; 2026 | พัฒนาเพื่อตรวจสอบคุณภาพอินเทอร์เน็ต</small>
    </footer>

    <script>
        const ispKeywords = {
            'TRUE': { name: 'TRUE Online', color: '#ff6b35', url: 'https://www.trueinternet.co.th/' },
            '3BB': { name: '3BB', color: '#00a8e8', url: 'https://www.3bb.co.th/' },
            'AIS': { name: 'AIS Fibre', color: '#8b5cf6', url: 'https://www.ais.th/fibre' },
            'DTAC': { name: 'DTAC', color: '#ec4899', url: 'https://www.dtac.co.th/' },
            'CAT': { name: 'CAT Telecom', color: '#10b981', url: 'https://www.cattelecom.com/' },
            'TOT': { name: 'TOT', color: '#f59e0b', url: 'https://www.tot.co.th/' },
            'MESH': { name: 'Mesh WiFi', color: '#06b6d4', url: '#' },
            'ASUS': { name: 'ASUS Router', color: '#dc2626', url: '#' },
            'TP-LINK': { name: 'TP-Link', color: '#ea580c', url: 'https://www.tp-link.com/th/' },
            'MI': { name: 'Mi WiFi', color: '#f97316', url: '#' },
            'D-LINK': { name: 'D-Link', color: '#2563eb', url: 'https://www.dlink.com/th/' },
            'SINGTEL': { name: 'Singtel', color: '#eab308', url: 'https://www.singtel.com/' },
            'MAXIS': { name: 'Maxis', color: '#ef4444', url: 'https://www.maxis.com.my/' },
            'STARHUB': { name: 'StarHub', color: '#0ea5e9', url: 'https://www.starhub.com/' }
        };

        let speedChart;
        let wifiSignalChart;
        let internetSpeedChart;
        let wifiSignalHistory = [];
        let internetSpeedHistory = [];
        let speedHistory = [];
        let testCount = 0;

        function togglePassword() {
            const passwordInput = document.getElementById('wifiPassword');
            const toggleIcon = document.getElementById('toggleIcon');
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                toggleIcon.className = 'fas fa-eye-slash';
            } else {
                passwordInput.type = 'password';
                toggleIcon.className = 'fas fa-eye';
            }
        }

        function onSSIDChange() {
            const ssidSelect = document.getElementById('wifiSSID');
            const selectedOption = ssidSelect.options[ssidSelect.selectedIndex];
            const security = selectedOption.dataset.security;
            
            if (security) {
                const securitySelect = document.getElementById('wifiSecurity');
                if (security.includes('WPA') || security.includes('WPA2')) {
                    securitySelect.value = 'WPA';
                } else if (security.includes('WEP')) {
                    securitySelect.value = 'WEP';
                } else {
                    securitySelect.value = 'Open';
                }
            }
        }

        async function connectToWifi(event) {
            event.preventDefault();
            
            const btn = document.getElementById('connectBtn');
            const statusDiv = document.getElementById('connectStatus');
            const ssid = document.getElementById('wifiSSID').value;
            const username = document.getElementById('wifiUsername').value;
            const password = document.getElementById('wifiPassword').value;
            const security = document.getElementById('wifiSecurity').value;
            const saveConfig = document.getElementById('saveConfig').checked;
            
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>กำลังเชื่อมต่อ...';
            
            statusDiv.style.display = 'block';
            statusDiv.className = 'mt-3 alert alert-info';
            statusDiv.innerHTML = '<i class="fas fa-info-circle me-2"></i>กำลังเชื่อมต่อไปยัง WiFi: ' + ssid + '...';
            
            try {
                const response = await fetch('/api/connect', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        ssid: ssid,
                        username: username,
                        password: password,
                        security: security,
                        save: saveConfig
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    statusDiv.className = 'mt-3 alert alert-success';
                    statusDiv.innerHTML = '<i class="fas fa-check-circle me-2"></i>' + data.message;
                } else {
                    statusDiv.className = 'mt-3 alert alert-danger';
                    statusDiv.innerHTML = '<i class="fas fa-times-circle me-2"></i>' + data.message;
                }
                
            } catch (error) {
                statusDiv.className = 'mt-3 alert alert-warning';
                statusDiv.innerHTML = '<i class="fas fa-exclamation-triangle me-2"></i>ไม่สามารถเชื่อมต่อได้: ' + error.message + '<br><small>หมายเหตุ: การเชื่อมต่อ WiFi ต้องรันด้วยสิทธิ์ Admin</small>';
            }
            
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-plug me-2"></i>เชื่อมต่อ WiFi';
        }

        async function scanWifi() {
            const btn = document.getElementById('scanBtn');
            const wifiResults = document.getElementById('wifiResults');
            const wifiLoading = document.getElementById('wifiLoading');
            const wifiStatus = document.getElementById('wifiStatus');
            
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Scanning...';
            wifiLoading.style.display = 'block';
            wifiStatus.textContent = 'กำลังค้นหา WiFi...';
            
            try {
                const response = await fetch('/api/wifi');
                const data = await response.json();
                
                wifiLoading.style.display = 'none';
                
                if (data.error && !data.networks) {
                    wifiStatus.textContent = 'เกิดข้อผิดพลาด: ' + data.error;
                    return;
                }
                
                document.getElementById('ipAddress').textContent = data.public_ip || 'N/A';
                document.getElementById('publicIp').textContent = data.public_ip || 'N/A';
                document.getElementById('ispName').innerHTML = '<span style="color: ' + (data.isp?.color || '#00d4ff') + '">' + (data.isp?.name || 'Unknown') + '</span>';
                document.getElementById('location').textContent = data.location || 'N/A';
                
                if (data.networks && data.networks.length > 0) {
                    let html = '';
                    const sortedNetworks = data.networks.sort((a, b) => b.signal - a.signal);
                    
                    const ssidSelect = document.getElementById('wifiSSID');
                    ssidSelect.innerHTML = '<option value="">-- เลือก WiFi --</option>';
                    
                    const networkMap = {};
                    
                    sortedNetworks.forEach((network, index) => {
                        const ssidName = network.ssid || 'Hidden Network';
                        const security = network.security || 'Open';
                        
                        if (!networkMap[ssidName]) {
                            networkMap[ssidName] = network;
                            const option = document.createElement('option');
                            option.value = ssidName;
                            option.textContent = ssidName + ' (' + security + ')';
                            option.dataset.security = security;
                            ssidSelect.appendChild(option);
                        }
                        
                        const signalPercent = network.signal || 0;
                        let signalColor = '#ef4444';
                        let signalIcon = 'fa-signal-1';
                        if (signalPercent >= 75) {
                            signalColor = '#10b981';
                            signalIcon = 'fa-signal';
                        } else if (signalPercent >= 50) {
                            signalColor = '#f59e0b';
                            signalIcon = 'fa-signal-2';
                        } else if (signalPercent >= 25) {
                            signalColor = '#f97316';
                            signalIcon = 'fa-signal-3';
                        }
                        
                        const isSecure = network.security && network.security !== 'Open';
                        const lockIcon = isSecure ? 'fa-lock' : 'fa-lock-open';
                        const securityColor = isSecure ? '#10b981' : '#ef4444';
                        
                        html += '<div class="col-md-6 col-lg-4 mb-3">' +
                            '<div class="wifi-card glass-card p-3">' +
                                '<div class="d-flex justify-content-between align-items-start mb-2">' +
                                    '<div>' +
                                        '<h6 class="mb-1 text-truncate" style="max-width: 180px;">' + (network.ssid || 'Hidden Network') + '</h6>' +
                                        '<small class="text-muted">' + (network.bssid || '') + '</small>' +
                                    '</div>' +
                                    '<div class="text-end">' +
                                        '<i class="fas ' + signalIcon + '" style="color: ' + signalColor + '; font-size: 1.2rem;"></i>' +
                                        '<div style="color: ' + signalColor + '; font-weight: 600;">' + signalPercent + '%</div>' +
                                    '</div>' +
                                '</div>' +
                                '<div class="d-flex justify-content-between align-items-center">' +
                                    '<div>' +
                                        '<small><i class="fas ' + lockIcon + ' me-1" style="color: ' + securityColor + '"></i>' + (network.security || 'Open') + '</small>' +
                                        (network.channel ? '<small class="ms-2"><i class="fas fa-broadcast-tower me-1"></i>CH ' + network.channel + '</small>' : '') +
                                    '</div>' +
                                    '<div class="signal-bar" style="width: 60px; height: 6px; background: rgba(255,255,255,0.2); border-radius: 3px; overflow: hidden;">' +
                                        '<div style="width: ' + signalPercent + '%; height: 100%; background: ' + signalColor + ';"></div>' +
                                    '</div>' +
                                '</div>' +
                            '</div>' +
                        '</div>';
                    });
                    
                    wifiResults.innerHTML = html;
                    wifiStatus.textContent = 'พบ ' + data.networks.length + ' เครือข่าย WiFi';
                    
                    updateWifiSignalChart(sortedNetworks);
                } else {
                    wifiStatus.textContent = 'ไม่พบเครือข่าย WiFi หรือต้องรันด้วยสิทธิ์ Admin';
                }
                
            } catch (error) {
                wifiLoading.style.display = 'none';
                wifiStatus.textContent = 'เกิดข้อผิดพลาด: ' + error.message;
            }
            
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-sync-alt me-1"></i> Scan WiFi';
        }

        function updateWifiSignalChart(networks) {
            const topNetworks = networks.slice(0, 5);
            const labels = topNetworks.map(n => n.ssid || 'Hidden');
            const data = topNetworks.map(n => n.signal || 0);
            const colors = data.map(signal => {
                if (signal >= 75) return '#10b981';
                if (signal >= 50) return '#f59e0b';
                if (signal >= 25) return '#f97316';
                return '#ef4444';
            });
            
            wifiSignalChart.data.labels = labels;
            wifiSignalChart.data.datasets[0].data = data;
            wifiSignalChart.data.datasets[0].backgroundColor = colors;
            wifiSignalChart.update();
        }
        
        function updateInternetSpeedChart(speed) {
            const time = new Date().toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' });
            internetSpeedHistory.push({ time: time, speed: speed });
            
            if (internetSpeedHistory.length > 10) {
                internetSpeedHistory.shift();
            }
            
            internetSpeedChart.data.labels = internetSpeedHistory.map(h => h.time);
            internetSpeedChart.data.datasets[0].data = internetSpeedHistory.map(h => h.speed);
            internetSpeedChart.update();
        }

        async function getLocalIP() {
            try {
                const pc = new RTCPeerConnection();
                pc.createDataChannel('');
                await pc.createOffer();
                await pc.setLocalDescription(pc);
                
                return new Promise((resolve) => {
                    pc.onicecandidate = (ice) => {
                        if (ice && ice.candidate && ice.candidate.candidate) {
                            const ip = ice.candidate.candidate.split(' ')[4];
                            resolve(ip);
                            pc.close();
                        }
                    };
                    setTimeout(() => resolve('ไม่สามารถดึงได้'), 2000);
                });
            } catch {
                return 'ไม่สามารถดึงได้';
            }
        }

        async function fetchNetworkInfo() {
            try {
                const response = await fetch('/api/ipinfo');
                const data = await response.json();
                
                document.getElementById('ipAddress').textContent = data.ip || 'N/A';
                document.getElementById('publicIp').textContent = data.ip || 'N/A';
                
                let ispName = data.org || 'Unknown';
                let ispColor = '#6b7280';
                let ispUrl = '#';
                
                for (const [key, isp] of Object.entries(ispKeywords)) {
                    if (ispName.toUpperCase().includes(key)) {
                        ispName = isp.name;
                        ispColor = isp.color;
                        ispUrl = isp.url;
                        break;
                    }
                }
                
                document.getElementById('ispName').innerHTML = '<span style="color: ' + ispColor + '">' + ispName + '</span>';
                document.getElementById('location').textContent = (data.city || 'N/A') + ', ' + (data.country_code || '');
                
                const networkType = navigator.connection ? 
                    (navigator.connection.effectiveType || 'Unknown') : 'Unknown';
                document.getElementById('networkType').textContent = networkType.toUpperCase();
                
            } catch (error) {
                console.error('Error fetching network info:', error);
                document.getElementById('ipAddress').textContent = 'ไม่สามารถดึงได้';
                document.getElementById('ispName').textContent = 'ไม่ทราบ';
                document.getElementById('location').textContent = 'ไม่ทราบ';
            }
        }

        async function getLocalIPAddress() {
            const localIp = await getLocalIP();
            document.getElementById('localIp').textContent = localIp;
        }

        function getBrowserInfo() {
            const ua = navigator.userAgent;
            let browser = 'Unknown';
            
            if (ua.indexOf('Chrome') > -1) browser = 'Chrome';
            else if (ua.indexOf('Safari') > -1) browser = 'Safari';
            else if (ua.indexOf('Firefox') > -1) browser = 'Firefox';
            else if (ua.indexOf('Edge') > -1) browser = 'Edge';
            
            document.getElementById('browser').textContent = browser;
        }

        function getSystemInfo() {
            document.getElementById('platform').textContent = navigator.platform;
            document.getElementById('language').textContent = navigator.language;
            document.getElementById('timezone').textContent = Intl.DateTimeFormat().resolvedOptions().timeZone;
            document.getElementById('currentDate').textContent = new Date().toLocaleString('th-TH');
        }

        function initChart() {
            const ctx = document.getElementById('speedChart').getContext('2d');
            speedChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'ความเร็ว (Mbps)',
                        data: [],
                        borderColor: '#00d4ff',
                        backgroundColor: 'rgba(0, 212, 255, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: '#00d4ff',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        pointRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: { color: '#fff' }
                        }
                    },
                    scales: {
                        x: {
                            ticks: { color: 'rgba(255,255,255,0.7)' },
                            grid: { color: 'rgba(255,255,255,0.1)' }
                        },
                        y: {
                            beginAtZero: true,
                            ticks: { color: 'rgba(255,255,255,0.7)' },
                            grid: { color: 'rgba(255,255,255,0.1)' },
                            title: {
                                display: true,
                                text: 'Mbps',
                                color: 'rgba(255,255,255,0.7)'
                            }
                        }
                    }
                }
            });
            
            const wifiCtx = document.getElementById('wifiSignalChart').getContext('2d');
            wifiSignalChart = new Chart(wifiCtx, {
                type: 'bar',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'สัญญาณ WiFi (%)',
                        data: [],
                        backgroundColor: [],
                        borderColor: '#10b981',
                        borderWidth: 1,
                        borderRadius: 5
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    indexAxis: 'y',
                    plugins: {
                        legend: {
                            labels: { color: '#fff' }
                        }
                    },
                    scales: {
                        x: {
                            beginAtZero: true,
                            max: 100,
                            ticks: { color: 'rgba(255,255,255,0.7)' },
                            grid: { color: 'rgba(255,255,255,0.1)' },
                            title: {
                                display: true,
                                text: 'ความแรง (%)',
                                color: 'rgba(255,255,255,0.7)'
                            }
                        },
                        y: {
                            ticks: { color: 'rgba(255,255,255,0.7)' },
                            grid: { color: 'rgba(255,255,255,0.1)' }
                        }
                    }
                }
            });
            
            const internetCtx = document.getElementById('internetSpeedChart').getContext('2d');
            internetSpeedChart = new Chart(internetCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'ความเร็ว Internet (Mbps)',
                        data: [],
                        borderColor: '#f59e0b',
                        backgroundColor: 'rgba(245, 158, 11, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: '#f59e0b',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        pointRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: { color: '#fff' }
                        }
                    },
                    scales: {
                        x: {
                            ticks: { color: 'rgba(255,255,255,0.7)' },
                            grid: { color: 'rgba(255,255,255,0.1)' }
                        },
                        y: {
                            beginAtZero: true,
                            ticks: { color: 'rgba(255,255,255,0.7)' },
                            grid: { color: 'rgba(255,255,255,0.1)' },
                            title: {
                                display: true,
                                text: 'Mbps',
                                color: 'rgba(255,255,255,0.7)'
                            }
                        }
                    }
                }
            });
        }

        async function startSpeedTest() {
            const btn = document.getElementById('startTest');
            const speedCircle = document.getElementById('speedCircle');
            const speedValue = document.getElementById('speedValue');
            
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>กำลังทดสอบ...';
            
            const circumference = 2 * Math.PI * 85;
            const maxSpeed = 500;
            
            try {
                const testUrls = [
                    'https://speed.cloudflare.com/__down?bytes=10000000',
                    'https://proof.ovh.net/files/1Mb.dat'
                ];
                
                let totalSpeed = 0;
                let tests = 0;
                
                for (const url of testUrls) {
                    try {
                        const startTime = performance.now();
                        const response = await fetch(url);
                        const blob = await response.blob();
                        const endTime = performance.now();
                        
                        const duration = (endTime - startTime) / 1000;
                        const sizeInBits = blob.size * 8;
                        const speedBps = sizeInBits / duration;
                        const speedMbps = speedBps / 1000000;
                        
                        totalSpeed += speedMbps;
                        tests++;
                        break;
                    } catch (e) {
                        console.log('Test URL failed, trying next...');
                    }
                }
                
                if (tests === 0) {
                    for (let i = 0; i < 3; i++) {
                        const startTime = performance.now();
                        await fetch('https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png');
                        const endTime = performance.now();
                        
                        const duration = (endTime - startTime) / 1000;
                        const estimatedSpeed = (150 * 8) / (duration * 1000000);
                        totalSpeed += estimatedSpeed;
                        tests++;
                    }
                }
                
                const avgSpeed = tests > 0 ? totalSpeed / tests : 0;
                const finalSpeed = Math.round(avgSpeed * 10) / 10;
                
                testCount++;
                speedHistory.push(finalSpeed);
                
                const time = new Date().toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' });
                speedChart.data.labels.push('ครั้งที่ ' + testCount);
                speedChart.data.datasets[0].data.push(finalSpeed);
                
                if (speedChart.data.labels.length > 10) {
                    speedChart.data.labels.shift();
                    speedChart.data.datasets[0].data.shift();
                }
                speedChart.update();
                
                let currentSpeed = 0;
                const interval = setInterval(() => {
                    currentSpeed += finalSpeed / 20;
                    if (currentSpeed >= finalSpeed) {
                        currentSpeed = finalSpeed;
                        clearInterval(interval);
                        updateInternetSpeedChart(finalSpeed);
                    }
                    
                    const offset = circumference - (currentSpeed / maxSpeed) * circumference;
                    speedCircle.style.strokeDashoffset = offset;
                    speedValue.textContent = Math.round(currentSpeed * 10) / 10;
                }, 50);
                
            } catch (error) {
                console.error('Speed test error:', error);
                alert('เกิดข้อผิดพลาดในการทดสอบความเร็ว');
            }
            
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-redo me-2"></i>ทดสอบอีกครั้ง';
        }

        window.addEventListener('online', () => {
            document.getElementById('connectionStatus').className = 'status-indicator status-online';
            document.getElementById('connectionText').textContent = 'เชื่อมต่อแล้ว';
        });

        window.addEventListener('offline', () => {
            document.getElementById('connectionStatus').className = 'status-indicator status-offline';
            document.getElementById('connectionText').textContent = 'ไม่มีการเชื่อมต่อ';
        });

        window.addEventListener('load', () => {
            fetchNetworkInfo();
            getLocalIPAddress();
            getBrowserInfo();
            getSystemInfo();
            initChart();
        });

        if (navigator.connection) {
            navigator.connection.addEventListener('change', () => {
                const networkType = navigator.connection.effectiveType || 'Unknown';
                document.getElementById('networkType').textContent = networkType.toUpperCase();
            });
        }
    </script>
</body>
</html>
'''


def get_windows_wifi():
    try:
        result = subprocess.run(
            ['netsh', 'wlan', 'show', 'networks', 'mode=bssid'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        networks = []
        current_network = {}
        
        for line in result.stdout.split('\n'):
            line = line.strip()
            
            if 'SSID' in line and 'BSSID' not in line:
                if current_network:
                    networks.append(current_network)
                ssid = line.split(':')[1].strip() if ':' in line else ''
                current_network = {'ssid': ssid, 'bssid': '', 'signal': 0, 'channel': '', 'security': '', 'auth': ''}
            
            elif 'BSSID' in line:
                bssid = line.split(':')[1].strip() if ':' in line else ''
                current_network['bssid'] = bssid
            
            elif 'Signal' in line:
                try:
                    signal = line.split(':')[1].strip().replace('%', '')
                    current_network['signal'] = int(signal)
                except:
                    pass
            
            elif 'Channel' in line:
                try:
                    channel = line.split(':')[1].strip()
                    current_network['channel'] = channel
                except:
                    pass
            
            elif 'Authentication' in line:
                auth = line.split(':')[1].strip() if ':' in line else ''
                current_network['auth'] = auth
            
            elif 'Cipher' in line:
                cipher = line.split(':')[1].strip() if ':' in line else ''
                current_network['security'] = cipher
        
        if current_network and current_network.get('ssid'):
            networks.append(current_network)
        
        return networks
    except Exception as e:
        return {'error': str(e)}


def get_linux_wifi():
    try:
        result = subprocess.run(
            ['nmcli', '-t', '-f', 'SSID,SIGNAL,SECURITY,CHAN,FREQ', 'device', 'wifi', 'list', '--rescan', 'yes'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        networks = []
        for line in result.stdout.split('\n'):
            if line.strip():
                parts = line.split(':')
                if len(parts) >= 2:
                    ssid = parts[0]
                    signal = int(parts[1]) if parts[1].isdigit() else 0
                    security = parts[2] if len(parts) > 2 else ''
                    channel = parts[3] if len(parts) > 3 else ''
                    freq = parts[4] if len(parts) > 4 else ''
                    
                    if ssid:
                        networks.append({
                            'ssid': ssid,
                            'bssid': '',
                            'signal': signal,
                            'channel': channel,
                            'security': security,
                            'auth': security
                        })
        
        return networks
    except Exception as e:
        try:
            result = subprocess.run(
                ['iwlist', 'scan'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            networks = []
            current = {}
            
            for line in result.stdout.split('\n'):
                line = line.strip()
                
                if 'Cell ' in line:
                    if current.get('ssid'):
                        networks.append(current)
                    current = {'bssid': '', 'ssid': '', 'signal': 0, 'channel': '', 'security': '', 'auth': ''}
                
                elif 'Address:' in line:
                    current['bssid'] = line.split(':')[1].strip()
                
                elif 'ESSID:' in line:
                    ssid = line.split('"')[1] if '"' in line else ''
                    current['ssid'] = ssid
                
                elif 'Signal level' in line:
                    try:
                        match = re.search(r'Signal level[=:](\s*-?\d+)', line)
                        if match:
                            current['signal'] = int(match.group(1))
                    except:
                        pass
            
            if current.get('ssid'):
                networks.append(current)
            
            return networks
        except:
            return {'error': str(e)}


def get_public_ip_info():
    try:
        with urllib.request.urlopen('https://ipapi.co/json/', timeout=5) as response:
            data = json.loads(response.read().decode())
            return data
    except:
        return {}


def get_isp_links(isp_name):
    isp_links = {
        'TRUE': {'name': 'TRUE Online', 'url': 'https://www.trueinternet.co.th/', 'color': '#ff6b35'},
        '3BB': {'name': '3BB', 'url': 'https://www.3bb.co.th/', 'color': '#00a8e8'},
        'AIS': {'name': 'AIS Fibre', 'url': 'https://www.ais.th/fibre', 'color': '#8b5cf6'},
        'DTAC': {'name': 'DTAC', 'url': 'https://www.dtac.co.th/', 'color': '#ec4899'},
        'CAT': {'name': 'CAT Telecom', 'url': 'https://www.cattelecom.com/', 'color': '#10b981'},
        'TOT': {'name': 'TOT', 'url': 'https://www.tot.co.th/', 'color': '#f59e0b'},
    }
    
    isp_name_upper = isp_name.upper()
    for key, isp in isp_links.items():
        if key in isp_name_upper:
            return isp
    
    return {'name': isp_name, 'url': '#', 'color': '#6b7280'}


def scan_wifi():
    system = platform.system()
    
    if system == 'Windows':
        networks = get_windows_wifi()
    elif system == 'Linux':
        networks = get_linux_wifi()
    else:
        networks = {'error': f'Unsupported OS: {system}'}
    
    public_info = get_public_ip_info()
    
    isp_info = public_info.get('org', 'Unknown ISP')
    isp_data = get_isp_links(isp_info)
    
    result = {
        'platform': system,
        'networks': networks if isinstance(networks, list) else [],
        'error': networks.get('error') if isinstance(networks, dict) else None,
        'public_ip': public_info.get('ip', 'N/A'),
        'isp': isp_data,
        'location': f"{public_info.get('city', 'N/A')}, {public_info.get('country', 'N/A')}",
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    return result


def connect_wifi(ssid, username, password, security, save):
    system = platform.system()
    
    try:
        if system == 'Windows':
            if security == 'Open':
                result = subprocess.run(
                    ['netsh', 'wlan', 'connect', 'name=' + ssid],
                    capture_output=True,
                    text=True
                )
            else:
                result = subprocess.run(
                    ['netsh', 'wlan', 'connect', 'name=' + ssid],
                    capture_output=True,
                    text=True
                )
            
            if result.returncode == 0:
                return {'success': True, 'message': f'เชื่อมต่อ {ssid} สำเร็จ'}
            else:
                return {'success': False, 'message': 'ไม่สามารถเชื่อมต่อได้ กรุณาตรวจสอบ SSID และ Password'}
        
        elif system == 'Linux':
            if username:
                result = subprocess.run(
                    ['nmcli', 'dev', 'wifi', 'connect', ssid, 'password', password, 'username', username],
                    capture_output=True,
                    text=True
                )
            else:
                result = subprocess.run(
                    ['nmcli', 'dev', 'wifi', 'connect', ssid, 'password', password],
                    capture_output=True,
                    text=True
                )
            
            if result.returncode == 0:
                return {'success': True, 'message': f'เชื่อมต่อ {ssid} สำเร็จ'}
            else:
                return {'success': False, 'message': 'ไม่สามารถเชื่อมต่อได้ กรุณาตรวจสอบ SSID และ Password'}
        
        return {'success': False, 'message': f'ระบบปฏิบัติการ {system} ไม่รองรับ'}
    
    except Exception as e:
        return {'success': False, 'message': str(e)}


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/wifi')
def api_wifi():
    return jsonify(scan_wifi())


@app.route('/api/ipinfo')
def api_ipinfo():
    return jsonify(get_public_ip_info())


@app.route('/api/connect', methods=['POST'])
def api_connect():
    data = request.json
    return jsonify(connect_wifi(
        data.get('ssid', ''),
        data.get('username', ''),
        data.get('password', ''),
        data.get('security', 'WPA'),
        data.get('save', False)
    ))


if __name__ == '__main__':
    print('=' * 50)
    print('WiFi & Network Scanner')
    print('=' * 50)
    print('Starting server...')
    print('Open browser: http://localhost:5000')
    print('Press Ctrl+C to stop')
    print('=' * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
