module(..., package.seeall);

require('Body')
require('fsm')
require('gcm')

require('bodyIdle')
require('bodyStart')
require('bodyStop')
require('bodyReady')
require('bodyAnnass')

require{'bodyChase')
require('bodyApproach')
require('bodyKick')
require('bodyOrbit')
require('bodyGotoCenter')
require('bodyPosition')

require('bodyHalt')
require('bodyRight')
require('bodyLeft')

sm = fsm.new(bodyIdle); -- dont mess
sm:add_state(bodyStart); -- dont mess
sm:add_state(bodyStop); -- dont mess
sm:add_state(bodyReady); -- dont mess
sm:add_state(bodyAnnass);
sm:add_state(bodyApproach);
sm:add_state(bodyKick);
sm:add_state(bodyOrbit);
sm:add_state(bodyGotoCenter);
sm:add_state(bodyPosition);
sm:add_state(bodyHalt);
sm:add_state(bodyRight);
sm:add_state(bodyLeft);

sm:set_transition(bodyStart, 'done', bodyAnnass); -- ANNASS
sm:set_transition(bodyAnnass, 'done', bodyPosition); -- dont mess

--continuous left-right movement
sm:set_transition(bodyPosition, 'timeout', bodyGotoCenter);
sm:set_transition(bodyPosition, 'ballClose', bodyChase);
sm:set_transition(bodyPosition, 'ballLost', bodyGotoCenter);

sm:set_transition(bodyGotoCenter, 'ballFound', bodyHalt);
sm:set_transition(bodyGotoCenter, 'done', bodyHalt);
sm:set_transition(bodyGotoCenter, 'timeout', bodyGotoCenter);
sm:set_transition(bodyGotoCenter, 'ballClose', bodyChase);

sm:set_transition(bodyHalt, 'gotime', bodyLeft);
sm:set_transition(bodyLeft, 'right', bodyRight);
sm:set_transition(bodyRight, 'left', bodyLeft);

--abandon left-right movement if ball is close
sm:set_transition(bodyPosition, 'ballClose', bodyChase);
sm:set_transition(bodyHalt, 'ballClose', bodyChase);
sm:set_transition(bodyLeft, 'ballClose', bodyChase);
sm:set_transition(bodyRight, 'ballClose', bodyChase);

--chase the ball then orbit or go back to left right
sm:set_transition(bodyChase, 'ballClose', bodyOrbit);
sm:set_transition(bodyChase, 'ballFar', bodyGotoCenter);
sm:set_transition(bodyChase, 'ballLost', bodyGotoCenter);
sm:set_transition(bodyChase, 'timeout', bodyGotoCenter);

--orbit (no problem because ball should be in goal)
sm:set_transition(bodyOrbit, 'timeout', bodyGotoCenter);
sm:set_transition(bodyOrbit, 'ballLost', bodyGotoCenter);
sm:set_transition(bodyOrbit, 'ballFar', bodyGotoCenter);
sm:set_transition(bodyOrbit, 'done', bodyApproach);

--kick!
sm:set_transition(bodyApproach, 'ballFar', bodyGotoCenter);
sm:set_transition(bodyApproach, 'ballLost', bodyGotoCenter);
sm:set_transition(bodyApproach, 'timeout', bodyGotoCenter);
sm:set_transition(bodyApproach, 'kick', bodyKick);

-- set state debug handle to shared memory settor
sm:set_state_debug_handle(gcm.set_fsm_body_state, gcm.set_fsm_body_next_state);


function entry()
  sm:entry()
end

function update()
  sm:update();
end

function exit()
  sm:exit();
end
