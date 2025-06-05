document.addEventListener('DOMContentLoaded', function() {
    const canvas = document.getElementById('wallCanvas');
    const ctx = canvas.getContext('2d');
    const wallWidthInput = document.getElementById('wallWidth');
    const wallHeightInput = document.getElementById('wallHeight');
    const obstaclesContainer = document.getElementById('obstacles-container');
    const addObstacleBtn = document.getElementById('add-obstacle');
    const calculatePathBtn = document.getElementById('calculate-path');
    const playPathBtn = document.getElementById('play-path');
    const stopPathBtn = document.getElementById('stop-path');
    const timeDisplay = document.getElementById('time-display');
    const trajectoryList = document.getElementById('trajectory-list');
    
    let currentTrajectory = null;
    let animationId = null;
    let playStartTime = null;
    
    // Add obstacle
    addObstacleBtn.addEventListener('click', function() {
        const obstacleDiv = document.createElement('div');
        obstacleDiv.className = 'obstacle';
        obstacleDiv.innerHTML = `
            <div class="form-group">
                <label>X (m):</label>
                <input type="number" class="obs-x" value="1" step="0.1" min="0">
            </div>
            <div class="form-group">
                <label>Y (m):</label>
                <input type="number" class="obs-y" value="1" step="0.1" min="0">
            </div>
            <div class="form-group">
                <label>Width (m):</label>
                <input type="number" class="obs-width" value="0.25" step="0.01" min="0.1">
            </div>
            <div class="form-group">
                <label>Height (m):</label>
                <input type="number" class="obs-height" value="0.25" step="0.01" min="0.1">
            </div>
            <button class="remove-obstacle">Remove</button>
        `;
        obstaclesContainer.appendChild(obstacleDiv);
        
        // Add remove event listener
        obstacleDiv.querySelector('.remove-obstacle').addEventListener('click', function() {
            obstacleDiv.remove();
        });
    });
    
    // Calculate path
    calculatePathBtn.addEventListener('click', async function() {
        const wallWidth = parseFloat(wallWidthInput.value);
        const wallHeight = parseFloat(wallHeightInput.value);
        
        // Collect obstacles
        const obstacles = [];
        document.querySelectorAll('.obstacle').forEach(obstacleEl => {
            obstacles.push({
                x: parseFloat(obstacleEl.querySelector('.obs-x').value),
                y: parseFloat(obstacleEl.querySelector('.obs-y').value),
                width: parseFloat(obstacleEl.querySelector('.obs-width').value),
                height: parseFloat(obstacleEl.querySelector('.obs-height').value)
            });
        });
        
        try {
            const response = await fetch('/api/trajectories/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    wall_width: wallWidth,
                    wall_height: wallHeight,
                    obstacles: obstacles
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to calculate path');
            }
            
            currentTrajectory = await response.json();
            timeDisplay.textContent = `Coverage Time: ${currentTrajectory.coverage_time.toFixed(2)}s`;
            drawWallAndPath();
            loadTrajectories();
        } catch (error) {
            alert('Error: ' + error.message);
            console.error(error);
        }
    });
    
    // Play path
    playPathBtn.addEventListener('click', function() {
        if (!currentTrajectory || !currentTrajectory.trajectory || currentTrajectory.trajectory.length === 0) {
            alert('No path to play');
            return;
        }
        
        playPathBtn.disabled = true;
        stopPathBtn.disabled = false;
        playStartTime = Date.now();
        
        // Clear any existing animation
        if (animationId) {
            cancelAnimationFrame(animationId);
        }
        
        // Start animation
        animatePath();
    });
    
    // Stop path
    stopPathBtn.addEventListener('click', function() {
        playPathBtn.disabled = false;
        stopPathBtn.disabled = true;
        
        if (animationId) {
            cancelAnimationFrame(animationId);
            animationId = null;
        }
        
        // Redraw the full path
        drawWallAndPath();
    });
    
    // Animation function
    function animatePath() {
        const now = Date.now();
        const elapsed = (now - playStartTime) / 1000; // in seconds
        const totalTime = currentTrajectory.coverage_time;
        
        if (elapsed >= totalTime) {
            // Animation complete
            playPathBtn.disabled = false;
            stopPathBtn.disabled = true;
            drawWallAndPath();
            return;
        }
        
        // Find the current position in the trajectory
        const progress = elapsed / totalTime;
        const pathIndex = Math.floor(progress * (currentTrajectory.trajectory.length - 1));
        const currentPoint = currentTrajectory.trajectory[pathIndex];
        
        // Redraw
        drawWallAndPath(currentPoint);
        
        // Continue animation
        animationId = requestAnimationFrame(animatePath);
    }
    
    // Draw wall and path
    function drawWallAndPath(currentPoint = null) {
        const wallWidth = currentTrajectory ? currentTrajectory.wall_width : parseFloat(wallWidthInput.value);
        const wallHeight = currentTrajectory ? currentTrajectory.wall_height : parseFloat(wallHeightInput.value);
        
        // Calculate scale to fit wall in canvas
        const scale = Math.min(
            canvas.width / (wallWidth * 1.1), 
            canvas.height / (wallHeight * 1.1)
        );
        
        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Draw wall
        ctx.strokeStyle = '#000';
        ctx.lineWidth = 2;
        ctx.strokeRect(
            (canvas.width - wallWidth * scale) / 2,
            (canvas.height - wallHeight * scale) / 2,
            wallWidth * scale,
            wallHeight * scale
        );
        
        // Draw obstacles
        if (currentTrajectory && currentTrajectory.obstacles) {
            ctx.fillStyle = 'rgba(200, 0, 0, 0.5)';
            currentTrajectory.obstacles.forEach(obstacle => {
                ctx.fillRect(
                    (canvas.width - wallWidth * scale) / 2 + obstacle.x * scale,
                    (canvas.height - wallHeight * scale) / 2 + obstacle.y * scale,
                    obstacle.width * scale,
                    obstacle.height * scale
                );
            });
        }
        
        // Draw path if available
        if (currentTrajectory && currentTrajectory.trajectory) {
            const path = currentTrajectory.trajectory;
            const offsetX = (canvas.width - wallWidth * scale) / 2;
            const offsetY = (canvas.height - wallHeight * scale) / 2;
            
            // Draw complete path in light gray
            ctx.beginPath();
            ctx.moveTo(offsetX + path[0].x * scale, offsetY + path[0].y * scale);
            for (let i = 1; i < path.length; i++) {
                ctx.lineTo(offsetX + path[i].x * scale, offsetY + path[i].y * scale);
            }
            ctx.strokeStyle = 'rgba(0, 0, 0, 0.2)';
            ctx.lineWidth = 1;
            ctx.stroke();
            
            // Draw traveled path in blue if animating --gpt
            if (currentPoint) {
                const currentIndex = path.findIndex(p => 
                    p.x === currentPoint.x && p.y === currentPoint.y
                );
                
                if (currentIndex > 0) {
                    ctx.beginPath();
                    ctx.moveTo(offsetX + path[0].x * scale, offsetY + path[0].y * scale);
                    for (let i = 1; i <= currentIndex; i++) {
                        ctx.lineTo(offsetX + path[i].x * scale, offsetY + path[i].y * scale);
                    }
                    ctx.strokeStyle = 'blue';
                    ctx.lineWidth = 2;
                    ctx.stroke();
                }
                
                // current position as a circle drawing -- source gpt
                ctx.beginPath();
                ctx.arc(
                    offsetX + currentPoint.x * scale,
                    offsetY + currentPoint.y * scale,
                    3, 0, Math.PI * 2
                );
                ctx.fillStyle = 'red';
                ctx.fill();
            }
        }
    }
    
    // previous trajectories loding it 
    async function loadTrajectories() {
        try {
            const response = await fetch('/api/trajectories/');
            if (!response.ok) {
                throw new Error('Failed to load trajectories');
            }
            
            const trajectories = await response.json();
            trajectoryList.innerHTML = '';
            
            trajectories.forEach(traj => {
                const trajEl = document.createElement('div');
                trajEl.className = 'trajectory-item';
                trajEl.innerHTML = `
                    <strong>Wall:</strong> ${traj.wall_width}m × ${traj.wall_height}m | 
                    <strong>Obstacles:</strong> ${traj.obstacles.length} | 
                    <strong>Time:</strong> ${traj.coverage_time.toFixed(2)}s
                `;
                
                trajEl.addEventListener('click', () => {
                    currentTrajectory = traj;
                    timeDisplay.textContent = `Coverage Time: ${traj.coverage_time.toFixed(2)}s`;
                    drawWallAndPath();
                });
                
                trajectoryList.appendChild(trajEl);
            });
        } catch (error) {
            console.error('Error loading trajectories:', error);
        }
    }
    
    loadTrajectories();
});