create or replace view weekly_sales_shrinkage as
select
    i.sku,
    i.name,
    i.category,
    date_trunc('week', s.created_at) as sales_week,
    sum(s.quantity) as units_sold,
    round(sum(s.quantity * i.price)::numeric, 2) as gross_sales,
    round(sum(s.quantity * (i.price - i.cost))::numeric, 2) as estimated_margin,
    greatest(
        coalesce(sum(sh.quantity), 0) - coalesce(sum(s.quantity), 0) - max(i.quantity_on_hand),
        0
    ) as estimated_shrinkage_units
from items i
left join sales s on s.item_id = i.id
left join shipments sh on sh.item_id = i.id
group by i.sku, i.name, i.category, date_trunc('week', s.created_at);
