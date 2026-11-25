// Opens a fellow's card when their tile is selected, and closes it again.
// Each card is a <dialog>, so the Escape key and focus handling come for free.

document.querySelectorAll("[data-opens]").forEach((tile) => {
  tile.addEventListener("click", () => {
    const card = document.getElementById(tile.dataset.opens);
    if (card) card.showModal();
  });
});

document.querySelectorAll("dialog.fellow-card").forEach((card) => {
  card.querySelector("[data-closes]").addEventListener("click", () => card.close());
  // Close when someone clicks the dimmed background around the card.
  card.addEventListener("click", (event) => {
    if (event.target !== card) return;
    const box = card.getBoundingClientRect();
    const inside =
      event.clientX >= box.left && event.clientX <= box.right &&
      event.clientY >= box.top && event.clientY <= box.bottom;
    if (!inside) card.close();
  });
});
