require('main_copy');
require('serialization');

function sendImg()
  -- yuyv --
  yuyv = vcm.get_image_yuyv();
  width = vcm.get_image_width()/2; -- number of yuyv packages
  height = vcm.get_image_height();
  count = vcm.get_image_count();
  
  array = serialization.serialize_array(yuyv, width, height, 'int32', 'yuyv', count);
  sendyuyv = {};
  sendyuyv.team = {};
  sendyuyv.team.number = gcm.get_team_number();
  sendyuyv.team.player_id = gcm.get_team_player_id();
  
  local f = assert(io.open("image.raw", "w"));

  for i=1,#array do
    sendyuyv.arr = array[i];
    f:write(array[i].data);
    --print(serialization.serialize(sendyuyv));
    -- Need to sleep in order to stop drinking out of firehose
    --unix.usleep(pktDelay);
   -- print(array[i]);
  end
  f:close();

end

sendImg();
