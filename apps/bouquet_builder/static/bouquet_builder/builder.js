document.addEventListener("DOMContentLoaded", () => {
  const format = new Intl.NumberFormat("ru-RU", { maximumFractionDigits: 0 });
  const components = [...document.querySelectorAll(".component")];
  const packaging = [...document.querySelectorAll('input[name="packaging"]')];
  const list = document.querySelector("#composition");
  const total = document.querySelector("#total-price");
  function refresh() {
    let amount = 0;
    const items = [];
    components.forEach((card) => {
      const quantity = Number(card.querySelector("input").value) || 0;
      if (!quantity) return;
      const price = Number(card.dataset.price);
      amount += price * quantity;
      items.push([card.dataset.name, quantity, price * quantity]);
    });
    const selected = packaging.find((item) => item.checked);
    if (selected) amount += Number(selected.dataset.price || 0);
    list.innerHTML = items.length ? items.map(([name, quantity, price]) => `<li><span>${name} × ${quantity}</span><b>${format.format(price)} ₽</b></li>`).join("") : '<li class="muted">Выберите цветы для композиции</li>';
    total.textContent = `${format.format(amount)} ₽`;
  }
  components.forEach((card) => card.querySelector("input").addEventListener("input", refresh));
  packaging.forEach((item) => item.addEventListener("change", refresh));
  refresh();
});
