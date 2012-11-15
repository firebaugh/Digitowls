require('Motion')
require('Body')
require('walk')
require('vector')
require('Config')
require('wcm')
require('gcm')
require('util')

t0 = 0;
timeout = 10.0;

ballNear = 0.85;

tLost = 6.0;

-- maximum walk velocity
maxStep = 0.06;

function entry()
  print(_NAME.." entry");

  Motion.sm:set_state('stance');

  t0 = Body.get_time();
end

function update()
  local t = Body.get_time();

  --walk left
  walk.set_velocity(0,maxStep,0);

  -- get ball pose
  ball = wcm.get_ball();
  ballR = math.sqrt(ball.x^2 + ball.y^2);
  tBall = Body.get_time() - ball.t;

  -- If ball is close, abandon goal to chase it down --
  if ((tBall < 3.0) and (ballR < ballNear)) then
    return "ballClose";
  end
  -- lost ball
  if ((t - t0 > 1.0) and (t - ball.t > tLost)) then
    return "left";
  end
  -- timeout
  if (t - t0 > timeout) then
    return "left";
  end
end

function exit()
end

