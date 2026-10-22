/**
 * CLEATS Radar Chart Visualizer (Pure Canvas implementation)
 * 6 Axes: Completeness (C), Latency (L), Engagement (E), Accuracy (A), Transparency (T), Standardization (S)
 */

function drawCLEATSRadar(canvasId, scores) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  const dpr = window.devicePixelRatio || 1;

  // Set display size and internal resolution for Retina displays
  const size = 240;
  canvas.width = size * dpr;
  canvas.height = size * dpr;
  canvas.style.width = `${size}px`;
  canvas.style.height = `${size}px`;
  ctx.scale(dpr, dpr);

  const centerX = size / 2;
  const centerY = size / 2;
  const radius = (size / 2) - 34;

  const axes = [
    { key: 'completeness', label: 'C', fullName: 'Completeness', val: scores.completeness || 0 },
    { key: 'latency', label: 'L', fullName: 'Latency', val: scores.latency || 0 },
    { key: 'engagement', label: 'E', fullName: 'Engagement', val: scores.engagement || 0 },
    { key: 'accuracy', label: 'A', fullName: 'Accuracy', val: scores.accuracy || 0 },
    { key: 'transparency', label: 'T', fullName: 'Transparency', val: scores.transparency || 0 },
    { key: 'standardization', label: 'S', fullName: 'Standardization', val: scores.standardization || 0 }
  ];

  const totalAxes = axes.length;
  const angleStep = (Math.PI * 2) / totalAxes;

  ctx.clearRect(0, 0, size, size);

  // 1. Draw concentric background polygon grids (2, 4, 6, 8, 10)
  const levels = [2, 4, 6, 8, 10];
  levels.forEach(level => {
    const levelRadius = (level / 10) * radius;
    ctx.beginPath();
    for (let i = 0; i < totalAxes; i++) {
      const angle = (i * angleStep) - (Math.PI / 2);
      const x = centerX + Math.cos(angle) * levelRadius;
      const y = centerY + Math.sin(angle) * levelRadius;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.strokeStyle = level === 10 ? 'rgba(255, 255, 255, 0.15)' : 'rgba(255, 255, 255, 0.05)';
    ctx.lineWidth = 1;
    ctx.stroke();
  });

  // 2. Draw axis lines and labels
  axes.forEach((axis, i) => {
    const angle = (i * angleStep) - (Math.PI / 2);
    const endX = centerX + Math.cos(angle) * radius;
    const endY = centerY + Math.sin(angle) * radius;

    // Axis line
    ctx.beginPath();
    ctx.moveTo(centerX, centerY);
    ctx.lineTo(endX, endY);
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
    ctx.stroke();

    // Axis label (C, L, E, A, T, S)
    const labelX = centerX + Math.cos(angle) * (radius + 18);
    const labelY = centerY + Math.sin(angle) * (radius + 18);

    ctx.font = '600 12px "Outfit", sans-serif';
    ctx.fillStyle = axis.val === 0 ? '#ef4444' : '#94a3b8';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(axis.label, labelX, labelY);
  });

  // 3. Draw radar data polygon
  const hasZero = axes.some(a => a.val === 0);
  const dataPoints = [];

  ctx.beginPath();
  axes.forEach((axis, i) => {
    const angle = (i * angleStep) - (Math.PI / 2);
    const r = (Math.max(0, Math.min(10, axis.val)) / 10) * radius;
    const x = centerX + Math.cos(angle) * r;
    const y = centerY + Math.sin(angle) * r;
    dataPoints.push({ x, y, val: axis.val, label: axis.label });

    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.closePath();

  // Polygon fill & stroke
  const grad = ctx.createRadialGradient(centerX, centerY, 5, centerX, centerY, radius);
  if (hasZero) {
    grad.addColorStop(0, 'rgba(239, 68, 68, 0.25)');
    grad.addColorStop(1, 'rgba(99, 102, 241, 0.15)');
    ctx.strokeStyle = '#f87171';
  } else {
    grad.addColorStop(0, 'rgba(99, 102, 241, 0.35)');
    grad.addColorStop(1, 'rgba(56, 189, 248, 0.15)');
    ctx.strokeStyle = '#818cf8';
  }

  ctx.fillStyle = grad;
  ctx.fill();
  ctx.lineWidth = 2;
  ctx.stroke();

  // 4. Draw data point vertices with zero-highlight dots
  dataPoints.forEach(pt => {
    ctx.beginPath();
    ctx.arc(pt.x, pt.y, pt.val === 0 ? 5 : 3.5, 0, Math.PI * 2);
    if (pt.val === 0) {
      ctx.fillStyle = '#ef4444';
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 1.5;
      ctx.fill();
      ctx.stroke();
    } else {
      ctx.fillStyle = '#38bdf8';
      ctx.fill();
    }
  });
}
