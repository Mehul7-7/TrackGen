document.addEventListener('DOMContentLoaded', function(){
  const video = document.getElementById('ad-video');
  const btn = document.getElementById('ad-continue');
  if(video){
    video.addEventListener('ended', function(){
      btn.disabled = false;
      btn.classList.remove('opacity-50');
      fetch('/api/ad_watched', {method:'POST'}).then(r=>r.json()).then(()=> {
        document.getElementById('ad-modal').style.display = 'none';
      });
    });
  }
});

function checkKeyword(keyword, site){
  fetch('/api/check_keyword', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({keyword: keyword, site: site})
  }).then(r=>r.json()).then(data=>{
    alert('Keyword: '+data.keyword + '\nMentioned: '+data.mentioned+'\nCited: '+data.cited+'\nEngine: '+data.engine);
    location.reload();
  }).catch(e=>{
    alert('Error checking keyword');
  });
}
