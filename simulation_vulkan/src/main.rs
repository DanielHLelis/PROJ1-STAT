mod shader;


use bytemuck::{Zeroable, Pod};
#[repr(C)]
#[derive(Default, Copy, Clone, Zeroable, Pod)]
pub struct Machine {
    pub position: [f32; 4],
}

vulkano::impl_vertex!(Machine, position);

extern crate rand;
extern crate rand_pcg;
use rand::prelude::*;

fn main() {
    let seed = 1;
    let n = 10;
    let p0 = 0.9;
    let tr = 1000;
    let beta = 0;
    let s = 10;

    let mut seed_generator = rand_pcg::Pcg64::seed_from_u64(seed);
    let sim_per_batch = 32;


    // ##################################################
    // 01| VULKAN BOILER PLATE 
    // ##################################################

    // CRIANDO UMA INSTANCIA DE UM 'APP' VULKAN
    use vulkano::instance::{Instance, InstanceCreateInfo};

    let instance = Instance::new(InstanceCreateInfo::default()).expect("failed to create instance");

    // ANALIZANDO DISPOSITIVOS VULKAN DISPONÍVEIS
    use vulkano::device::physical::PhysicalDevice;

    let physical = PhysicalDevice::enumerate(&instance).next().expect("no device available");

    // CRIANDO UMA QUEUE FAMILY
    let queue_family = physical.queue_families()
        .find(|&q| q.supports_graphics())
        .expect("couldn't find a graphical queue family");

    // CRIANDO UM DEVICE
    use vulkano::device::{Device, QueueCreateInfo, DeviceCreateInfo};

    let (device, mut queues) = Device::new(
        physical,
        DeviceCreateInfo {
            // here we pass the desired queue families that we want to use
            queue_create_infos: vec![QueueCreateInfo::family(queue_family)],
            ..Default::default()
        },
    )
        .expect("failed to create device");

    // ESCOLHENDO UMA QUEUE
    let queue = queues.next().unwrap();


    // ##################################################
    // 02| CRIANDO UM BUFFER
    // ##################################################
    use vulkano::buffer::{BufferUsage, CpuAccessibleBuffer};
    use vulkano::command_buffer::{AutoCommandBufferBuilder, CommandBufferUsage};
    use vulkano::sync::{self, GpuFuture};

    // CRIANDO UM NOVO BUFFER
    let bufsize = sim_per_batch * (n + s + 1);
    let mut data_iter : Vec<Machine> = (0..bufsize).map(|_| Machine{position: [2.0, 0.0, {let mut x = seed_generator.next_u64() as f32; while std::f32::NAN == x {x = seed_generator.next_u64() as f32;} x}, 0.0]}).collect();

    let uni_buffer = CpuAccessibleBuffer::from_data(
        device.clone(), 
        BufferUsage::all(), 
        false,
        Machine {position: [n as f32, p0 as f32, tr as f32, beta as f32]}
    )
    .expect("failed to create buffer");

    let sim_data_model = [4.0, n as f32, 0.0, 0.0];
    for i in 0..sim_per_batch {
        data_iter[i].position = sim_data_model;
    }

    //let mut n_counter = 0;
    let working_machine_model = [1.0, p0 as f32, seed as f32, 0.0];

    for i in sim_per_batch..(n * sim_per_batch + 1) {
        data_iter[i].position = working_machine_model;
        data_iter[i].position[2] = {let mut x = seed_generator.next_u64() as f32; while std::f32::NAN == x {x = seed_generator.next_u64() as f32;} x};
    }

    let data_buffer = CpuAccessibleBuffer::from_iter(
        device.clone(), 
        BufferUsage::all(), 
        false, 
        data_iter
    )
        .expect("failed to create buffer");


    // ##################################################
    // 06) PIPELINES
    // ##################################################
    // CARREGANDO O SHADER
    let shader = shader::load(device.clone())
        .expect("failed to create shader module");

    // CRIANDO A PIPE LINE
    use vulkano::pipeline::ComputePipeline;

    let compute_pipeline = ComputePipeline::new(
        device.clone(),
        shader.entry_point("main").unwrap(),
        &(),
        None,
        |_| {},
    )
        .expect("failed to create compute pipeline");


    // ##################################################
    // 07) DESCRIPTORS
    // ##################################################
    // CRIANDO UM DESCRIPTOR
    use vulkano::pipeline::Pipeline;
    use vulkano::descriptor_set::{PersistentDescriptorSet, WriteDescriptorSet};

    let layout = compute_pipeline.layout().set_layouts().get(0).unwrap();
    let set = PersistentDescriptorSet::new(
        layout.clone(),
        [WriteDescriptorSet::buffer(0, data_buffer.clone()), WriteDescriptorSet::buffer(1, uni_buffer.clone())], // 0 is the binding
    )
        .unwrap();


    // ##################################################
    // 08) DISPATCH
    // ##################################################
    // CRIANDO O BUILDER
    // use vulkano::command_buffer::{AutoCommandBufferBuilder, CommandBufferUsage};
    use vulkano::pipeline::PipelineBindPoint;
    
    let mut collapse_counter : u64 = 0;
    let mut collapse : Vec<u64> =  (0..sim_per_batch).map(|_| 0).collect();


    //for i in 1..2 {
    for clk in 0..100u64 {
        if sim_per_batch as u64 <= collapse_counter {break;}

        let mut builder = AutoCommandBufferBuilder::primary(
            device.clone(),
            queue.family(),
            CommandBufferUsage::MultipleSubmit,
        )
        .unwrap();

        // JUNTANDO O PIPELINE AO BUILDER
        builder
            .bind_pipeline_compute(compute_pipeline.clone())
            .bind_descriptor_sets(
                PipelineBindPoint::Compute,
                compute_pipeline.layout().clone(),
                0, // 0 is the index of our set
                set.clone(),
            )
            .dispatch([1024, 1, 1])
            .unwrap();

        // CRIANDO O BUFFER DE COMANDOS
        let command_buffer = builder.build().unwrap();

        // SICRONIZANDO COM A GPU
        if clk != 0 
        {let future = sync::now(device.clone())
            .then_execute(queue.clone(), command_buffer)
            .unwrap()
            .then_signal_fence_and_flush()
            .unwrap();

        // ESPERANDO A EXECUÇÃO
        future.wait(None).unwrap();}

        // CHECANDO SE A EXECUÇÃO FOI BEM SUCEDIDA
        let content = data_buffer.read().unwrap();

        println!("CLOCK {:?}", clk);
        println!("SIM STATE");
        for i in 0..sim_per_batch {
            println!("{:?}", content[i].position);
            let current_n = content[i].position[1] as i64;
            let current_broken = content[i].position[2] as i64;
            let valid_machines = current_n + (s as i64) - current_broken;
            println!("Valid machines: {:?}", valid_machines);
            let collapse_happend = valid_machines < n as i64;
            if collapse_happend && 0 == collapse[i] {
                collapse[i] = clk;
                collapse_counter += 1;
            }
        }

        for (n, val) in content.iter().enumerate() {
            println!("{:?} | {:?} ", n, val.position);
        }
    }

    println!("\n\n\nRESULT: ");
    println!("Collapse counter: {:?} ", collapse_counter);
    println!("Collapse state:");
    println!("{:?}", collapse);

    println!("Everything succeeded!");
}
