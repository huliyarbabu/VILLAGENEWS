const modal = document.getElementById("modal");
const openModal = document.getElementById("openModal");
const openModal2 = document.getElementById("openModal2");
const closeModal = document.getElementById("closeModal");

const newsForm = document.getElementById("newsForm");
const latest = document.getElementById("latest");
const related = document.getElementById("related");
const search = document.getElementById("search");

let newsData = [
  {
    title: "ಪೌತಿ ಖಾತೆ ಆಂದೋಲನ: ರೈತರಿಗೆ ದಾಖಲೆ ವಿತರಣೆ",
    content: "ಬುಕ್ಕಾಪಟ್ಟಣದಲ್ಲಿನ ಸಮುದಾಯ ಭವನದಲ್ಲಿ ರೈತರಿಗೆ ಪಹಣಿಗಳನ್ನು ವಿತರಿಸಲಾಯಿತು.",
    category: "ರೈತ ಸುದ್ದಿ",
    time: "ಇಂದು"
  },
  {
    title: "ಕೆಂಕೆರೆ ಪ್ರಕರಣ: ಆರೋಪಿಗಳು ವಶಕ್ಕೆ",
    content: "ತಮಿಳುನಾಡಿನ ನಾಲ್ವರು ಆರೋಪಿಗಳನ್ನು ಪೊಲೀಸರು ಬಂಧಿಸಿದ್ದಾರೆ.",
    category: "ಸ್ಥಳೀಯ",
    time: "ನಿನ್ನೆ"
  },
  {
    title: "SSLC ವಿದ್ಯಾರ್ಥಿಗಳಿಗೆ ಪ್ರೇರಣಾದಾಯಕ ಸಂದೇಶ",
    content: "ವಿದ್ಯಾರ್ಥಿಗಳಿಗೆ ಪರೀಕ್ಷಾ ತಯಾರಿ ಕುರಿತು ಮಾರ್ಗದರ್ಶನ ನೀಡಲಾಯಿತು.",
    category: "ಶಿಕ್ಷಣ",
    time: "2 ದಿನ ಹಿಂದೆ"
  }
];

let relatedData = [
  { title:"ರಾಗಿ ಖರೀದಿ ಕೇಂದ್ರ ಆರಂಭಕ್ಕೆ ರೈತರ ಪ್ರತಿಭಟನೆ", tag:"ರೈತ", img:"https://picsum.photos/400/260?1" },
  { title:"ಬ್ಯಾಂಕ್‌ನಲ್ಲಿ 10 ವರ್ಷ ಮೇಲ್ಪಟ್ಟ ಹಣ ವಾಪಸ್ ಪಡೆಯಲು ಮನವಿ", tag:"ಸಾರ್ವಜನಿಕ", img:"https://picsum.photos/400/260?2" },
  { title:"ಪಬ್ಲಿಕ್ ಫಸ್ಟ್ ಕನ್ನಡ ಲೋಕಾರ್ಪಣೆ ಕಾರ್ಯಕ್ರಮ", tag:"ಸ್ಥಳೀಯ", img:"https://picsum.photos/400/260?3" },
];

function renderLatest(list){
  latest.innerHTML = "";
  if(list.length === 0){
    latest.innerHTML = `<div class="news"><h4>ಯಾವುದೇ ಸುದ್ದಿ ಇಲ್ಲ</h4><p>ಹೊಸ ಸುದ್ದಿ ಹಾಕಿ.</p></div>`;
    return;
  }
  list.forEach(n=>{
    latest.innerHTML += `
      <div class="news">
        <span class="tag red">${n.category}</span>
        <h4>${n.title}</h4>
        <p>${n.content}</p>
        <div class="line">
          <span>📍 ಹುಳಿಯಾರು</span>
          <span>⏱️ ${n.time}</span>
        </div>
      </div>
    `;
  });
}

function renderRelated(){
  related.innerHTML = "";
  relatedData.forEach(r=>{
    related.innerHTML += `
      <div class="rel">
        <img src="${r.img}" alt="">
        <div>
          <span class="tag">${r.tag}</span>
          <h5>${r.title}</h5>
          <div class="meta">
            <span>👁️ 2.5k</span>
            <span>❤️ 390</span>
          </div>
        </div>
      </div>
    `;
  });
}

openModal.onclick = ()=> modal.style.display="block";
openModal2.onclick = ()=> modal.style.display="block";
closeModal.onclick = ()=> modal.style.display="none";
window.onclick = (e)=>{ if(e.target===modal) modal.style.display="none"; }

newsForm.addEventListener("submit",(e)=>{
  e.preventDefault();
  const title = document.getElementById("title").value.trim();
  const content = document.getElementById("content").value.trim();
  const category = document.getElementById("category").value;

  newsData.unshift({title, content, category, time:"ಈಗ"});
  renderLatest(newsData);

  newsForm.reset();
  modal.style.display="none";
});

search.addEventListener("input", (e)=>{
  const q = e.target.value.toLowerCase();
  const filtered = newsData.filter(n =>
    n.title.toLowerCase().includes(q) ||
    n.content.toLowerCase().includes(q) ||
    n.category.toLowerCase().includes(q)
  );
  renderLatest(filtered);
});

renderLatest(newsData);
renderRelated();
