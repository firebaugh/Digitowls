module(..., package.seeall);

require('Body')
require('walk')
require('vector')
require('util')
require('Config')
require('wcm')
require('Speak')
require('gcm')


-- maximum walk velocity
maxStep = 0.06;

function entry()
  print(_NAME.." entry");

end

function update()

  walk.set_velocity(0,maxStep,0);
  return "done";

end

function exit()
  print(_NAME..' exit');
end

